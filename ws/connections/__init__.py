"""
ws/connections — Publisher/viewer connection manager.
Full traceback logged on any error so root cause is always visible.
"""

import asyncio
import traceback
from utils.logging import logger

def _imports():
    from registry.publishers import publishers
    from registry.viewers    import viewers
    from registry.namespaces import namespaces
    from routing.matcher     import router
    from ws.frames           import (build_state_frame, build_heartbeat,
                                     build_error, parse_frame)
    from pairing             import pairing
    from storage.memory      import mem
    from storage.disk        import disk
    from storage.rolling     import rolling
    return (publishers, viewers, namespaces, router,
            build_state_frame, build_heartbeat, build_error, parse_frame,
            pairing, mem, disk, rolling)

HEARTBEAT_INTERVAL = 15


class ConnectionManager:

    async def handle_publisher(self, websocket, handshake: dict):
        pub_id    = handshake['id']
        namespace = handshake.get('namespace', 'default')

        # ── Resolve imports — catch failures here explicitly ──────
        try:
            (publishers, viewers, namespaces, router,
             build_state_frame, build_heartbeat, build_error, parse_frame,
             pairing, mem, disk, rolling) = _imports()
        except Exception:
            tb = traceback.format_exc()
            logger.error("publisher_import_failed",
                         pub_id=pub_id, traceback=tb)
            return

        try:
            publishers.register(pub_id, namespace, ws=websocket)
            namespaces.declare(namespace, owner_id=pub_id)
        except Exception:
            logger.error("publisher_register_failed", traceback=traceback.format_exc())
            return

        logger.info("publisher_connected", pub_id=pub_id, namespace=namespace)

        hb_task = asyncio.create_task(
            self._heartbeat_loop(websocket, pub_id, build_heartbeat)
        )

        try:
            async for raw in websocket:
                try:
                    parsed = parse_frame(raw)
                except Exception:
                    logger.error("parse_frame_crash", tb=traceback.format_exc())
                    continue

                if isinstance(parsed, dict):
                    ft = parsed.get('frame_type', '')
                    if ft == 'heartbeat':
                        publishers.heartbeat(pub_id)
                    elif ft in ('error', 'frame_decode'):
                        logger.warn("frame_error", detail=str(parsed)[:300])
                    continue

                # State frame
                frame = parsed
                frame.namespace    = namespace
                frame.publisher_id = pub_id

                errors = frame.validate()
                if errors:
                    logger.warn("invalid_frame", errors=errors)
                    try:
                        await websocket.send(
                            build_error("invalid_frame", "; ".join(errors))
                        )
                    except Exception:
                        pass
                    continue

                publishers.increment(pub_id)
                logger.info("frame_received",
                            pub=pub_id, ns=namespace,
                            keys=list(frame.json_state.keys()))

                try:
                    result = pairing.ingest_json(frame)
                    if result:
                        await self._dispatch(
                            result, viewers, namespaces, router,
                            build_state_frame, mem, disk, rolling
                        )
                    for stale in pairing.flush_stale():
                        await self._dispatch(
                            stale, viewers, namespaces, router,
                            build_state_frame, mem, disk, rolling
                        )
                except Exception:
                    logger.error("dispatch_error",
                                 ns=namespace,
                                 traceback=traceback.format_exc())

        except Exception:
            logger.error("publisher_connection_error",
                         pub_id=pub_id,
                         traceback=traceback.format_exc())
        finally:
            hb_task.cancel()
            publishers.unregister(pub_id)
            logger.info("publisher_disconnected", pub_id=pub_id)

    async def handle_viewer(self, websocket, handshake: dict):
        viewer_id    = handshake['id']
        subscription = handshake.get('subscription', '#')

        try:
            (publishers, viewers, namespaces, router,
             build_state_frame, build_heartbeat, build_error, parse_frame,
             pairing, mem, disk, rolling) = _imports()
        except Exception:
            logger.error("viewer_import_failed", traceback=traceback.format_exc())
            return

        viewers.register(viewer_id, ws=websocket, subscription=subscription)
        router.subscribe(viewer_id, subscription)
        logger.info("viewer_connected", viewer_id=viewer_id, sub=subscription)

        # Push any live state immediately on connect
        try:
            from routing.matcher import _match
            snapshot = mem.snapshot()
            for ns, frame in snapshot.items():
                if _match(ns, subscription):
                    await websocket.send(build_state_frame(frame))
        except Exception:
            pass

        hb_task = asyncio.create_task(
            self._heartbeat_loop(websocket, viewer_id, build_heartbeat)
        )

        try:
            async for raw in websocket:
                try:
                    parsed = parse_frame(raw)
                    if isinstance(parsed, dict) and parsed.get('frame_type') == 'heartbeat':
                        viewers.heartbeat(viewer_id)
                except Exception:
                    pass
        except Exception:
            logger.error("viewer_connection_error",
                         viewer_id=viewer_id,
                         traceback=traceback.format_exc())
        finally:
            hb_task.cancel()
            router.unsubscribe(viewer_id)
            viewers.unregister(viewer_id)
            logger.info("viewer_disconnected", viewer_id=viewer_id)

    async def _dispatch(self, frame, viewers, namespaces, router,
                         build_state_frame, mem, disk, rolling):
        mem.write(frame)

        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, disk.write, frame)
            await loop.run_in_executor(None, rolling.run_all, frame.namespace)
        except Exception as e:
            logger.warn("storage_write_failed", error=str(e))

        namespaces.declare(frame.namespace)
        matched_ids = router.resolve(frame.namespace)

        logger.info("dispatch",
                    ns=frame.namespace,
                    viewers_matched=len(matched_ids),
                    all_subs=router.all_subscriptions())

        if not matched_ids:
            logger.warn("no_matched_viewers", ns=frame.namespace)
            return

        wire  = build_state_frame(frame)
        tasks = [
            self._safe_send(viewers.ws_of(vid), wire, vid, viewers)
            for vid in matched_ids
            if viewers.ws_of(vid)
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_send(self, ws, data, viewer_id, viewers):
        try:
            await ws.send(data)
            viewers.increment(viewer_id)
            logger.info("frame_sent", viewer_id=viewer_id)
        except Exception as e:
            logger.warn("viewer_send_failed", viewer_id=viewer_id, error=str(e))

    async def _heartbeat_loop(self, websocket, client_id, build_heartbeat):
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            try:
                await websocket.send(build_heartbeat("server"))
            except Exception:
                break


conns = ConnectionManager()
