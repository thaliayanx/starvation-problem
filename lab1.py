import simpy
import random
import time
from random import randint

lock=0
req1=None
num_of_read=0
num_of_write=0
read_count=0
RANDOM_SEED = 42
NEW_REQUEST = 100  
INTERVAL = 10.0 
NUM_DATA_BLOCK=20


def source(env, number, interval, data):
    random.seed(time.clock())
    for i in range(number):
        j = random.uniform(0.0,1.0)
        duration=random.uniform(1,10)
        if j>0.5:
            c = action(env, 'read%d' % i, data)
        else:
            c = action(env, 'write%d' % i, data)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)

def action(env, name, data):
    global lock
    global req1
    global num_of_read
    global num_of_write
    global read_count
    arrive = env.now
    datablock=randint(0,NUM_DATA_BLOCK-1)
    print('%7.4f %s on datablock %d: Received' % (arrive, name, datablock))
    if lock == 0:
        #print('%7.4f %s: lock=0' % (env.now, name))
        if name[0]=='r':
            req1=data.request()
            num_of_read+=1
            yield req1
            print('%7.4f %s on datablock %d: in queue' % (env.now, name, datablock))
            duration = random.uniform(20,50)
            lock = 1
            yield env.timeout(duration)
            print('%7.4f %s on datablock %d: Finished' % (env.now, name, datablock))
            num_of_read-=1
            read_count+=1
        else:
            req=data.request()
            num_of_write+=1
            yield req
            print('%7.4f %s on datablock %d: in queue' % (env.now, name, datablock))
            wait = env.now - arrive
            print('%7.4f %s on datablock %d: Waited %7.3f' % (env.now, name, datablock, wait))
            duration = random.uniform(20,50)
            lock = 2
            yield env.timeout(duration)
            data.release(req)  
            num_of_write-=1
            lock=0    
            print('%7.4f %s on datablock %d: Finished' % (env.now, name, datablock))       
    elif lock == 1:
        #print('%7.4f %s: lock=1' % (env.now, name))
        if name[0]=='r':
            if read_count>3 and num_of_write>0:
                print('starvation happens')
                read_count=0
                lock=2
                data.release(req1)
                req=data.request()
                yield req
                print('%7.4f %s on datablock %d: in queue' % (env.now, name, datablock))
                duration = random.uniform(20,50)
                yield env.timeout(duration)
                print('%7.4f %s on datablock %d: Finished' % (env.now, name, datablock))
            else: 
                duration = random.uniform(20,50)
                num_of_read+=1
                yield env.timeout(duration)
                print('%7.4f %s on datablock %d: Finished' % (env.now, name, datablock))
                num_of_read-=1
                read_count+=1
                if num_of_read == 0:
                    data.release(req1)       
                    lock=0
        else:
            if read_count>3 and num_of_write>0:
                print('starvation happens')
                read_count=0
                lock=2
                data.release(req1)
                req=data.request()
                num_of_write+=1
                yield req
                print('%7.4f %s on datablock %d: in queue' % (env.now, name, datablock))
                duration = random.uniform(20,50)
                yield env.timeout(duration)
                num_of_write-=1
                print('%7.4f %s on datablock %d: Finished' % (env.now, name, datablock))
            else: 
                req=data.request()
                num_of_write+=1
                yield req
                print('%7.4f %s on datablock %d: in queue' % (env.now, name, datablock))
                wait = env.now - arrive
                print('%7.4f %s on datablock %d: Waited %7.3f' % (env.now, name, datablock, wait))
                duration = random.uniform(20,50)
                lock = 2
                yield env.timeout(duration)
                data.release(req)  
                num_of_write-=1
                lock=0
                print('%7.4f %s on datablock %d: Finished' % (env.now, name, datablock))
    else: 
        #print('%7.4f %s: lock=2' % (env.now, name))
        with data.request() as req:
            if name[0]=='r':
                yield req 
                print('%7.4f %s on datablock %d: in queue' % (env.now, name, datablock))
                wait = env.now - arrive
                print('%7.4f %s on datablock %d: Waited %7.4f' % (env.now, name, datablock, wait))
                duration = random.uniform(20,50)
                num_of_read+=1
                lock =1
                yield env.timeout(duration)
                print('%7.4f %s on datablock %d: Finished' % (env.now, name, datablock))
                num_of_read-=1
                read_count+=1
                lock=0
            else: 
                num_of_write+=1
                yield req
                print('%7.4f %s on datablock %d: in queue' % (env.now, name, datablock))
                wait = env.now - arrive
                print('%7.4f %s on datablock %d: Waited %7.4f' % (env.now, name, datablock, wait))
                duration = random.uniform(20,50)
                lock =2
                yield env.timeout(duration)
                print('%7.4f %s on datablock %d: Finished' % (env.now, name, datablock))
                num_of_write-=1
                lock=0
                
    

# Setup and start the simulation
print('Typical Reader and Writer')
env = simpy.Environment()

# Start processes and run
data = simpy.Resource(env, capacity=1)
env.process(source(env, NEW_REQUEST, INTERVAL, data))
env.run()
