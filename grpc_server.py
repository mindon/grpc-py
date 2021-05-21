from concurrent import futures
import time, math, logging, sys, os, importlib
import grpc

sys.path.append('./proto')
import task_pb2_grpc, task_pb2

sys.path.append('./demos')
# preload modules
# ------

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def fin(start, output=None, error=None):
  reply = task_pb2.TaskReply(start_at=start, stop_at=int(round(time.time() * 1000)))
  if error is None:
    reply.output = output
  else:
    reply.error = error
  return reply 

molduleStatus = {}
class TaskServicer(task_pb2_grpc.TaskServicer):
  def Run(self, req, ctx):
    logger.info(req)
    start = int(round(time.time() * 1000))
    output = ""
    m = None
    name = req.name
    forceReload = name[:1] == '!'
    if forceReload:
      name = name[1:]
    
    if len(req.path) > 0 and os.path.isdir(req.path) and not req.path in sys.path:
      sys.path.append(req.path)

    if importlib.util.find_spec(name) is None:
      return fin(start, error='module {} not found'.format(name))

    if name not in sys.modules:
      molduleStatus[name] = False
      try:
        m = importlib.import_module(name)
        molduleStatus[name] = True
      except Exception as e:
        del molduleStatus[name] # clean status
        logger.warning(e)
    else:
      m = sys.modules[name]
      if forceReload:
        molduleStatus[name] = False
        try:
          importlib.reload(m)
          molduleStatus[name] = True
        except Exception as e:
          del molduleStatus[name] # clean status
          logger.warning(e)
    
    if m is None:
      if name in molduleStatus:
        del molduleStatus[name] # clean status
      return fin(start, error='module {} import failed'.format(name))

    if len(req.func) > 0:
      if hasattr(m, req.func):
        mfunc = getattr(m, req.func)
        output = mfunc(req.input)
      else:
        if name in molduleStatus and not molduleStatus[name]:
          # wait first import ready
          while name in molduleStatus and not molduleStatus[name] and not hasattr(m, req.func):
            time.sleep(0.005)

          if hasattr(m, req.func):
            mfunc = getattr(m, req.func)
            output = mfunc(req.input)
          else:
            return fin(start, error='{} func not found'.format(req.func))
        else:
          return fin(start, error='{} func not found'.format(req.func))
    else:
      output = m.run(req.input)
    return fin(start, output=output)

def serve(addr = '[::]:50051'):
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

  task_pb2_grpc.add_TaskServicer_to_server(
    TaskServicer(), server)

  logger.info('Python ~ gRPC Service by Mindon at {}'.format(addr))
  assert int(addr.split(':')[-1]) > 0
  server.add_insecure_port(addr)
  server.start()
  server.wait_for_termination()
  # server.stop(None)


if __name__ == '__main__':
  FORMAT = '%(asctime)-15s %(message)s'
  logging.basicConfig(format=FORMAT)
  if len(sys.argv) > 1:
    serve(sys.argv[1])
  else:
    serve()
