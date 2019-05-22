# module to generate random baselines
# Run as: python slm_lab/spec/random_baseline.py
from slm_lab.lib import logger, util
import gym
import numpy as np
import pydash as ps


# extra envs to include
INCLUDE_ENVS = [
    'vizdoom-v0',
]
EXCLUDE_ENVS = [
    'CarRacing-v0',  # window bug
    'Reacher-v2',  # exclude mujoco
    'Pusher-v2',
    'Thrower-v2',
    'Striker-v2',
    'InvertedPendulum-v2',
    'InvertedDoublePendulum-v2',
    'HalfCheetah-v3',
    'Hopper-v3',
    'Swimmer-v3',
    'Walker2d-v3',
    'Ant-v3',
    'Humanoid-v3',
    'HumanoidStandup-v2',
    'FetchSlide-v1',
    'FetchPickAndPlace-v1',
    'FetchReach-v1',
    'FetchPush-v1',
    'HandReach-v0',
    'HandManipulateBlockRotateZ-v0',
    'HandManipulateBlockRotateParallel-v0',
    'HandManipulateBlockRotateXYZ-v0',
    'HandManipulateBlockFull-v0',
    'HandManipulateBlock-v0',
    'HandManipulateBlockTouchSensors-v0',
    'HandManipulateEggRotate-v0',
    'HandManipulateEggFull-v0',
    'HandManipulateEgg-v0',
    'HandManipulateEggTouchSensors-v0',
    'HandManipulatePenRotate-v0',
    'HandManipulatePenFull-v0',
    'HandManipulatePen-v0',
    'HandManipulatePenTouchSensors-v0',
    'FetchSlideDense-v1',
    'FetchPickAndPlaceDense-v1',
    'FetchReachDense-v1',
    'FetchPushDense-v1',
    'HandReachDense-v0',
    'HandManipulateBlockRotateZDense-v0',
    'HandManipulateBlockRotateParallelDense-v0',
    'HandManipulateBlockRotateXYZDense-v0',
    'HandManipulateBlockFullDense-v0',
    'HandManipulateBlockDense-v0',
    'HandManipulateBlockTouchSensorsDense-v0',
    'HandManipulateEggRotateDense-v0',
    'HandManipulateEggFullDense-v0',
    'HandManipulateEggDense-v0',
    'HandManipulateEggTouchSensorsDense-v0',
    'HandManipulatePenRotateDense-v0',
    'HandManipulatePenFullDense-v0',
    'HandManipulatePenDense-v0',
    'HandManipulatePenTouchSensorsDense-v0',
]
NUM_EVAL = 100


def enum_envs():
    '''Enumerate all the env names of the latest version'''
    envs = [es.id for es in gym.envs.registration.registry.all()]
    envs += INCLUDE_ENVS
    envs = ps.difference(envs, EXCLUDE_ENVS)
    return envs


def gen_random_return(env_name, seed):
    '''Generate a single-episode random policy return for an environment'''
    # TODO generalize for unity too once it has a gym wrapper
    env = gym.make(env_name)
    env.seed(seed)
    env.reset()
    done = False
    total_reward = 0
    while not done:
        _, reward, done, _ = env.step(env.action_space.sample())
        total_reward += reward
    return total_reward


def gen_random_baseline(env_name, num_eval=NUM_EVAL):
    '''Generate the random baseline for an environment by averaging over num_eval episodes'''
    returns = util.parallelize(gen_random_return, [(env_name, i) for i in range(num_eval)])
    mean_rand_ret = np.mean(returns)
    std_rand_ret = np.std(returns)
    return {'mean': mean_rand_ret, 'std': std_rand_ret}


def main():
    '''
    Main method to generate all random baselines and write to file.
    Run as: python slm_lab/spec/random_baseline.py
    '''
    filepath = 'slm_lab/spec/_random_baseline.json'
    old_random_baseline = util.read(filepath)
    random_baseline = {}
    envs = enum_envs()
    for idx, env_name in enumerate(envs):
        if env_name in old_random_baseline:
            logger.info(f'Using existing random baseline for {env_name}: {idx + 1}/{len(envs)}')
            random_baseline[env_name] = old_random_baseline[env_name]
        else:
            try:
                logger.info(f'Generating random baseline for {env_name}: {idx + 1}/{len(envs)}')
                random_baseline[env_name] = gen_random_baseline(env_name, NUM_EVAL)
            except Exception as e:
                logger.warning(f'Cannot start env: {env_name}, skipping random baseline generation')
                continue
        util.write(random_baseline, filepath)
    logger.info(f'Done, random baseline written to {filepath}')
    return random_baseline


if __name__ == '__main__':
    main()
