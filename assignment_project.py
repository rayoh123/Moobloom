# Rllib docs: https://docs.ray.io/en/latest/rllib.html

try:
    from malmo import MalmoPython
except:
    import MalmoPython

import sys
import time
import json
import math
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import randint
import random
import gym, ray
from gym.spaces import Discrete, Box
from ray.rllib.agents import ppo


class DiamondCollector(gym.Env):

    def __init__(self, env_config):  
        # Static Parameters
        self.size = 10
        self.reward_density = .1
        self.penalty_density = .02
        self.obs_size = 7
        self.max_episode_steps = 100
        self.log_frequency = 10
        self.action_dict = {
            0: 'move 1',  # Move one block forward
            1: 'turn 1',  # Turn 90 degrees to the right
            2: 'turn -1',  # Turn 90 degrees to the left
##            3: 'attack 1'  # Destroy block (Let's comment this command out for our sanity check to make it simpler.)
##                             We will add this and more commands later once we get our sanity check working.
##                             Right now, our sanity check will involve the agent simply trying to run away from the zombies
                                             
        }
        # Rllib Parameters

        self.action_space =  Discrete(len(self.action_dict)) 
        self.observation_space = Box(0, 1, shape=(self.obs_size * self.obs_size, ), dtype=np.float32)

        # Malmo Parameters
        self.agent_host = MalmoPython.AgentHost()
        try:
            self.agent_host.parse( sys.argv )
        except RuntimeError as e:
            print('ERROR:', e)
            print(self.agent_host.getUsage())
            exit(1)

        # DiamondCollector Parameters
        self.is_begin = True
        self.facing_zombie = False
        self.num_zombies = 40
        self.damage_taken_so_far = 0
        self.new_damage_taken = 0
        self.obs = None
        self.episode_step = 0
        self.episode_return = 0
        self.returns = []
        self.steps = []
        self.max_episode_steps = 300

    def reset(self):
        """
        Resets the environment for the next episode.

        Returns
            observation: <np.array> flattened initial obseravtion
        """
        # Reset Malmo
        world_state = self.init_malmo()

        # Reset Variables
        self.returns.append(self.episode_return)
        current_step = self.steps[-1] if len(self.steps) > 0 else 0
        self.steps.append(current_step + self.episode_step)
        self.episode_return = 0
        self.episode_step = 0

        # Log
        if len(self.returns) > self.log_frequency + 1 and \
            len(self.returns) % self.log_frequency == 0:
            self.log_returns()

        # Get Observation
        self.obs = self.get_observation(world_state)

        return self.obs

    def step(self, action):
        """
        Take an action in the environment and return the results.

        Args
            action: <int> index of the action to take

        Returns
            observation: <np.array> flattened array of obseravtion
            reward: <int> reward from taking action
            done: <bool> indicates terminal state
            info: <dict> dictionary of extra information
        """
        if self.is_begin:
            zombie_locations = set()   
            for i in range(self.num_zombies):
                x = random.randint(-self.size,self.size + 1)
                z = random.randint(-self.size,self.size + 1)
                while (x,z) in zombie_locations:
                    x = random.randint(-self.size,self.size + 1)
                    z = random.randint(-self.size,self.size + 1)
                zombie_locations.add((x,z))
            for loc in zombie_locations:
                self.agent_host.sendCommand(f'chat /summon zombie {loc[0]} 2 {loc[1]} {{Attributes:[{{Name:"generic.movementSpeed", Base:0.0}}]}}')
            self.is_begin = False

        # Get Action
        if not self.facing_zombie or (self.facing_zombie and action != 'move 1'):
            command = self.action_dict[action]
            self.agent_host.sendCommand(command)
            self.episode_step += 1

        # Get Observation
        world_state = self.agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)
        self.obs = self.get_observation(world_state) 

        # Get Done
        done = not world_state.is_mission_running 

        # Get Reward
        reward = 0
        for r in world_state.rewards:
            reward += r.getValue()
        reward -= self.new_damage_taken
        self.episode_return += reward
        

        return self.obs, reward, done, dict()

    def get_mission_xml(self):
#         # Draw walls around the arena
#         # Draw west wall
#         west_wall_xml = "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='stone'/>".format(-self.size-1, -self.size-1, self.size, -self.size) + \
#                         "<DrawCuboid x1='{}' x2='{}' y1='3' y2='3' z1='{}' z2='{}' type='stone'/>".format(-self.size-1, -self.size-1, self.size, -self.size)
#                         
#         east_wall_xml = "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='stone'/>".format(self.size+1, self.size+1, self.size, -self.size) + \
#                         "<DrawCuboid x1='{}' x2='{}' y1='3' y2='3' z1='{}' z2='{}' type='stone'/>".format(self.size+1, self.size+1, self.size, -self.size)
# 
#         north_wall_xml = "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='stone'/>".format(-self.size-1, self.size+1, self.size, self.size) + \
#                          "<DrawCuboid x1='{}' x2='{}' y1='3' y2='3' z1='{}' z2='{}' type='stone'/>".format(-self.size-1, self.size+1, self.size, self.size)
#                          
#         south_wall_xml = "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='stone'/>".format(-self.size-1, self.size+1, -self.size, -self.size) + \
#                          "<DrawCuboid x1='{}' x2='{}' y1='3' y2='3' z1='{}' z2='{}' type='stone'/>".format(-self.size-1, self.size+1, -self.size, -self.size)


##        zombies_xml = []
##        zombie_locations = set()
##   
##        for i in range(self.num_zombies):
##            x = random.randint(-self.size,self.size + 1)
##            z = random.randint(-self.size,self.size + 1)
##            while (x,z) in zombie_locations:
##                x = random.randint(-self.size,self.size + 1)
##                z = random.randint(-self.size,self.size + 1)
##            zombie_locations.add((x,z))
##            zombies_xml.append("<DrawEntity x='"+str(x)+"' y='2' z='"+str(z)+"' type='Zombie' />")
##         
##        zombies_xml = ''.join(zombies_xml)

        return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
                <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                    <About>
                        <Summary>Diamond Collector</Summary>
                    </About>

                    <ServerSection>
                        <ServerInitialConditions>
                            <Time>
                                <StartTime>18000</StartTime>
                                <AllowPassageOfTime>false</AllowPassageOfTime>
                            </Time>
                            <Weather>clear</Weather>
                            <AllowSpawning>false</AllowSpawning>
                        </ServerInitialConditions>
                        <ServerHandlers>
                            <FlatWorldGenerator generatorString="3;7,2;1;"/>
                            <DrawingDecorator>''' + \
                                "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='air'/>".format(-900, 900, -900, 900) + \
                                "<DrawCuboid x1='{}' x2='{}' y1='1' y2='1' z1='{}' z2='{}' type='stone'/>".format(-self.size, self.size, -self.size, self.size) + \
                                '''<DrawBlock x='0'  y='2' z='0' type='air' />
                            </DrawingDecorator>
                            <ServerQuitWhenAnyAgentFinishes/>
                        </ServerHandlers>
                    </ServerSection>

                    <AgentSection mode="Survival">
                        <Name>CS175DiamondCollector</Name>
                        <AgentStart>
                            <Placement x="0.5" y="2" z="0.5" pitch="45" yaw="0"/>
                            <Inventory>
                                <InventoryItem slot="0" type="diamond_pickaxe"/>
                            </Inventory>
                        </AgentStart>
                        <AgentHandlers>
                            <ObservationFromNearbyEntities>
                                <Range name="Zombie" xrange="3" yrange="1" zrange="3"/>
                            </ObservationFromNearbyEntities>
                            <RewardForTimeTaken initialReward="1" delta="+2" density="PER_TICK" />
                            <DiscreteMovementCommands/>
                            <ChatCommands/>
                            <ObservationFromFullStats/>
                            <ObservationFromRay/>
                            <ObservationFromGrid>
                                <Grid name="floorAll">
                                    <min x="-'''+str(int(self.obs_size/2))+'''" y="-1" z="-'''+str(int(self.obs_size/2))+'''"/>
                                    <max x="'''+str(int(self.obs_size/2))+'''" y="0" z="'''+str(int(self.obs_size/2))+'''"/>
                                </Grid>
                            </ObservationFromGrid>
                            <AgentQuitFromReachingCommandQuota total="'''+str(self.max_episode_steps)+'''" />
                        </AgentHandlers>
                    </AgentSection>
                </Mission>'''

    def init_malmo(self):
        """
        Initialize new malmo mission.
        """
        self.is_begin = True
        my_mission = MalmoPython.MissionSpec(self.get_mission_xml(), True)
        my_mission_record = MalmoPython.MissionRecordSpec()
        my_mission.requestVideo(800, 500)
        my_mission.setViewpoint(1)

        max_retries = 3
        my_clients = MalmoPython.ClientPool()
        my_clients.add(MalmoPython.ClientInfo('127.0.0.1', 10000)) # add Minecraft machines here as available

        for retry in range(max_retries):
            try:
                self.agent_host.startMission( my_mission, my_clients, my_mission_record, 0, 'DiamondCollector' )
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:", e)
                    exit(1)
                else:
                    time.sleep(2)
                    
        world_state = self.agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = self.agent_host.getWorldState()
            for error in world_state.errors:
                print("\nError:", error.text)

        return world_state

    def get_observation(self, world_state):
        """
        Use the agent observation API to get a flattened 1 x 5 x 5 grid around the agent. 
        The agent is in the center square facing up.

        Args
            world_state: <object> current agent world state

        Returns
            observation: <np.array> the state observation
        """
        
        obs = np.zeros((self.obs_size * self.obs_size, ))
        
        while world_state.is_mission_running:
            time.sleep(0.1)
            world_state = self.agent_host.getWorldState()
            if len(world_state.errors) > 0:
                raise AssertionError('Could not load grid.')

            if world_state.number_of_observations_since_last_state > 0:
                # First we get the json from the observation API
                msg = world_state.observations[-1].text
                observations = json.loads(msg)
                
                # Record any new damage that is taken for negative reward later
                damage_taken = observations['DamageTaken']
                self.new_damage_taken = damage_taken - self.damage_taken_so_far
                self.damage_taken_so_far = damage_taken

                # Get observation
                agent_location = None
                for entity in observations['Zombie']:
                    if entity['name'] == 'CS175DiamondCollector':
                        agent_location = (entity['x']+2, entity['z']+2)
                        break                   
                zombie_locations = list((agent_location[0]-entity['x'], agent_location[1]-entity['z']) for entity in observations['Zombie'] if entity['name'] == 'Zombie')                              
                for i in range(self.obs_size * self.obs_size):
                    obs[i] = False  
                    
                for x,z in zombie_locations:
                    obs[math.floor(x) + math.floor(z) * self.obs_size] = True 
                    
#                 grid = observations['floorAll']
#                 for i, x in enumerate(grid):
#                     obs[i] = x == 'diamond_ore' or x == 'lava'

                # Rotate observation with orientation of agent
                obs = obs.reshape((1, self.obs_size, self.obs_size))
                yaw = observations['Yaw']
                if yaw >= 225 and yaw < 315:
                    obs = np.rot90(obs, k=1, axes=(1, 2))
                elif yaw >= 315 or yaw < 45:
                    obs = np.rot90(obs, k=2, axes=(1, 2))
                elif yaw >= 45 and yaw < 135:
                    obs = np.rot90(obs, k=3, axes=(1, 2))
                obs = obs.flatten()

                # Check if there is a zombie in front of agent
                self.facing_zombie = observations['LineOfSight']['type'] == 'Zombie'
                
                break
        
        return obs

    def log_returns(self):
        """
        Log the current returns as a graph and text file

        Args:
            steps (list): list of global steps after each episode
            returns (list): list of total return of each episode
        """
        box = np.ones(self.log_frequency) / self.log_frequency
        returns_smooth = np.convolve(self.returns[1:], box, mode='same')
        plt.clf()
        plt.plot(self.steps[1:], returns_smooth)
        plt.title('Diamond Collector')
        plt.ylabel('Return')
        plt.xlabel('Steps')
        plt.savefig('returns.png')

        with open('returns.txt', 'w') as f:
            for step, value in zip(self.steps[1:], self.returns[1:]):
                f.write("{}\t{}\n".format(step, value)) 


if __name__ == '__main__':
    ray.init()
    trainer = ppo.PPOTrainer(env=DiamondCollector, config={
        'env_config': {},           # No environment parameters to configure
        'framework': 'torch',       # Use pyotrch instead of tensorflow
        'num_gpus': 0,              # We aren't using GPUs
        'num_workers': 0            # We aren't using parallelism
    })

    while True:
        print(trainer.train())
