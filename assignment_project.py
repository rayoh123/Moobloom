# Rllib docs: https://docs.ray.io/en/latest/rllib.html

try:
    from malmo import MalmoPython
except:
    import MalmoPython
import malmoutils
import sys
import time
from pathlib import Path
import json
import math
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import randint
import random
import gym, ray
from gym.spaces import Discrete, Box
from ray.rllib.agents import ppo

def safeStartMission(agent_host, my_mission, my_client_pool, my_mission_record, role, expID):
    print("Starting Mission {}.".format(role))
    max_retries = 5
    for retry in range(max_retries):
        try:
            agent_host.startMission(my_mission, my_client_pool, my_mission_record, role, expID)
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:", e)
                exit(1)
            else:
                time.sleep(2)

def safeWaitForStart(agent_hosts):
    start_flags = [False for a in agent_hosts]
    start_time = time.time()
    time_out = 230
    while not all(start_flags) and time.time() - start_time < time_out:
        states = [a.peekWorldState() for a in agent_hosts]
        start_flags = [w.has_mission_begun for w in states]
        errors = [e for w in states for e in w.errors]
        if len(errors) > 0:
            print("Errors waiting for mission start:")
            for e in errors:
                print(e.text)
            exit(1)
        time.sleep(0.1)
        print(".", end=" ")
    if time.time() - start_time >= time_out:
        print("Timed out while waiting for mission to start.")
        exit(1)
    print()
    print("Mission has started.")




class TheWalkingDead(gym.Env):

    def __init__(self, env_config):
        # Static Parameters
        self.size = 10
        self.obs_size = 9   # This is the size of the observation grid
        self.log_frequency = 10
        self.action_dict = {
            0: 'move 1',  # Move one block forward
            1: 'turn 1',  # Turn 90 degrees to the right
            2: 'turn -1',  # Turn 90 degrees to the left
        }
        # Rllib Parameters
        self.num_items_in_observation_array = 3
        self.action_space = Discrete(len(self.action_dict))
        self.observation_space = Box(0, 1, shape=(self.num_items_in_observation_array * self.obs_size * self.obs_size,), dtype=np.float32)

        # Malmo Parameters
        self.agent_host = MalmoPython.AgentHost()
        self.video_host = MalmoPython.AgentHost()
        try:
            self.agent_host.parse(sys.argv)
        except RuntimeError as e:
            print('ERROR:', e)
            print(self.agent_host.getUsage())
            exit(1)

        # TheWalkingDead Parameters
        self.facing_zombie = False
        self.facing_creeper = False
        self.facing_wall = False       
        self.num_zombies = 2
        self.num_creepers = 2
        self.num_sheeps = 3
        self.damage_taken_so_far = 0
        self.new_damage_taken = 0
        self.obs = None
        self.prev_observation = None
        self.episode_step = 0
        self.episode_return = 0
        self.returns = []
        self.steps = []
        self.max_episode_steps = 200

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
        # get night vision
        if self.episode_step == 1:
            self.agent_host.sendCommand('chat /effect @p night_vision 999 99')
            self.agent_host.sendCommand('chat /effect VideoAgent night_vision 999 99')
            
        # Get Action
        if action != 'move 1' or (not self.facing_creeper and not self.facing_zombie and not self.facing_wall):
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
        # Draw walls around the arena
        west_wall_xml = f"<DrawCuboid x1='{-self.size - 1}' x2='{-self.size - 1}' y1='2' y2='5' z1='{2*self.size + 1}' z2='{-self.size - 1}' type='end_portal_frame'/>"
        east_wall_xml = f"<DrawCuboid x1='{self.size + 1}' x2='{self.size + 1}' y1='2' y2='5' z1='{2*self.size + 1}' z2='{-self.size - 1}' type='end_portal_frame'/>"
        north_wall_xml = f"<DrawCuboid x1='{-self.size - 1}' x2='{self.size + 1}' y1='2' y2='5' z1='{2*self.size + 1}' z2='{2*self.size + 1}' type='end_portal_frame'/>"
        south_wall_xml = f"<DrawCuboid x1='{-self.size - 1}' x2='{self.size + 1}' y1='2' y2='5' z1='{-self.size - 1}' z2='{-self.size - 1}' type='end_portal_frame'/>"
        walls_xml = west_wall_xml + east_wall_xml + north_wall_xml + south_wall_xml

        finishline = ''
        z = 2*self.size
        for x in range(-self.size, self.size+1):
            finishline += f'<DrawBlock x=\'{x}\' y=\'1\' z = \'{z}\' type=\'diamond_block\' />'
            finishline += '\n' 

        def mob_drawer(entity_name: str, num_entities: int) -> str:
            creature_xml = []
            creature_locations = set([(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)])
            for i in range(num_entities):
                x = random.randint(-self.size + 2, self.size-1)
                z = random.randint(-self.size + 2, self.size-1)
                while (x, z) in creature_locations:
                    x = random.randint(-self.size + 2, self.size-1)
                    z = random.randint(-self.size + 2, self.size-1)
                creature_locations.add((x, z))
                creature_xml.append("<DrawEntity x='" + str(x) + "' y='2' z='" + str(z) + f"' type='{entity_name}' />")
            creature_xml = ''.join(creature_xml)
            return creature_xml

        zombies_xml = mob_drawer('Zombie', self.num_zombies)
        creepers_xml = mob_drawer('Creeper', self.num_creepers)
        sheeps_xml = mob_drawer('Sheep', self.num_sheep)

        return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
                <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                    <About>
                        <Summary>TheWalkingDead</Summary>
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
                                "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='air'/>".format(-300, 300, -300, 300) + \
                                "<DrawCuboid x1='{}' x2='{}' y1='1' y2='1' z1='{}' z2='{}' type='obsidian'/>".format(-self.size-100, self.size+100, -self.size-100, self.size+100) + \
                                walls_xml + \
                                zombies_xml + \
                                creepers_xml + \
                                sheeps_xml + \
                                finishline + \
                                '''<DrawBlock x='0'  y='2' z='0' type='air' />
                            </DrawingDecorator>
                            <ServerQuitWhenAnyAgentFinishes/>
                        </ServerHandlers>
                    </ServerSection>

                    <AgentSection mode="Survival">
                        <Name>TheWalkingDead</Name>
                        <AgentStart>
                            <Placement x="0.5" y="2" z="0.5" pitch="45" yaw="0"/>
                        </AgentStart>
                        <AgentHandlers>''' + \
                            f'''<ObservationFromNearbyEntities>
                                <Range name="Zombie" xrange="{self.obs_size//2}" yrange="1" zrange="{self.obs_size//2}"/>
                                <Range name="Creeper" xrange="{self.obs_size//2}" yrange="1" zrange="{self.obs_size//2}"/>
                                <Range name="Sheep" xrange="{self.obs_size//2}" yrange="1" zrange="{self.obs_size//2}"/>
                            </ObservationFromNearbyEntities>
                            <ObservationFromFullStats/>
                            <ObservationFromRay/>
                            <ObservationFromGrid>
                                <Grid name="floorAll">
                                    <min x="-'''+str(int(self.obs_size/2))+'''" y="2" z="-'''+str(int(self.obs_size/2))+'''"/>
                                    <max x="'''+str(int(self.obs_size/2))+'''" y="2" z="'''+str(int(self.obs_size/2))+'''"/>
                                </Grid>
                            </ObservationFromGrid>
                            <RewardForTouchingBlockType>
                                <Block type="diamond_block" reward="+300" />
                            </RewardForTouchingBlockType>
                            <RewardForTimeTaken initialReward="10" delta="+2" density="PER_TICK" />
                            <DiscreteMovementCommands/>
                            <ChatCommands/>
                            <AgentQuitFromReachingCommandQuota total="'''+str(self.max_episode_steps)+'''" />
                            <AgentQuitFromTouchingBlockType>
                                <Block type="diamond_block" />
                            </AgentQuitFromTouchingBlockType>
                        </AgentHandlers>
                    </AgentSection>

                    <AgentSection mode="Spectator">
                        <Name>VideoAgent</Name>
                        <AgentStart>
                            <Placement x="0" y="10" z="-5" pitch="60" yaw="0"/>
                        </AgentStart>
                        <AgentHandlers>
                            <DiscreteMovementCommands/>
                            <VideoProducer>
                                <Width>860</Width>
                                <Height>480</Height>
                            </VideoProducer>
                        </AgentHandlers>
                    </AgentSection>
                </Mission>'''


    def init_malmo(self):
        """
        Initialize new malmo mission.
        """
        self.is_begin = True
        malmoutils.parse_command_line(self.video_host)

        my_mission = MalmoPython.MissionSpec(self.get_mission_xml(), True)

        my_mission_record = MalmoPython.MissionRecordSpec()
        video_recording_spec = MalmoPython.MissionRecordSpec()
        my_mission.requestVideo(800, 500)
        my_mission.setViewpoint(1)

        my_clients = MalmoPython.ClientPool()
        my_clients.add(MalmoPython.ClientInfo('127.0.0.1', 10000)) # add Minecraft machines here as available
        my_clients.add(MalmoPython.ClientInfo('127.0.0.1', 10001))
        my_clients.add(MalmoPython.ClientInfo('127.0.0.1', 10002))

        safeStartMission(self.agent_host, my_mission, my_clients, my_mission_record, 0, '')
        safeStartMission(self.video_host, my_mission, my_clients, video_recording_spec, 1, '')
        safeWaitForStart([self.video_host, self.agent_host])

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
        
        obs = np.zeros((self.num_items_in_observation_array * self.obs_size * self.obs_size, ))
        
        while world_state.is_mission_running:
            time.sleep(0.1)
            world_state = self.agent_host.getWorldState()
            if len(world_state.errors) > 0:
                raise AssertionError('Could not load grid.')

            if world_state.number_of_observations_since_last_state > 0:
                # First we get the json from the observation API
                msg = world_state.observations[-1].text
                observations = json.loads(msg)
                i = 0
                while 'DamageTaken' not in observations or \
                'Zombie' not in observations or \
                'Creeper' not in observations or \
                'Sheep' not in observations or \
                'Yaw' not in observations or \
                'LineOfSight' not in observations:
                    i += 1
                    if i == 5:
                        observations = self.prev_observation
                        break
                    time.sleep(0.1)
                    msg = world_state.observations[-1].text
                    observations = json.loads(msg)
                    print(observations)
                    print(222222222222)
                
                self.prev_observation = observations
                # Record any new damage that is taken for negative reward later
                damage_taken = observations['DamageTaken']
                self.new_damage_taken = damage_taken - self.damage_taken_so_far
                self.damage_taken_so_far = damage_taken

                # Get observation
                agent_location = None
                for entity in observations['Zombie']:
                    if entity['name'] == 'TheWalkingDead':
                        agent_location = (entity['x']+self.obs_size//2, entity['z']+self.obs_size//2)
                        break                 

                # Get zombie locations  
                zombie_locations = list((agent_location[0]-entity['x'], agent_location[1]-entity['z']) for entity in observations['Zombie'] if entity['name'] == 'Zombie')                              
                for i in range(self.obs_size * self.obs_size):
                    obs[i] = False  
                    
                for x,z in zombie_locations:
                    obs[math.floor(z) + math.floor(x) * self.obs_size] = True 

                # Get creeper locations  
                creeper_locations = list((agent_location[0]-entity['x'], agent_location[1]-entity['z']) for entity in observations['Creeper'] if entity['name'] == 'Creeper')                              
                for i in range(self.obs_size ** 2, 2 * self.obs_size ** 2):
                    obs[i] = False  
                    
                for x,z in creeper_locations:
                    obs[self.obs_size ** 2 + math.floor(z) + math.floor(x) * self.obs_size] = True 
                
                 # Get sheep locations  
                sheep_locations = list((agent_location[0]-entity['x'], agent_location[1]-entity['z']) for entity in observations['Sheep'] if entity['name'] == 'Sheep')                              
                for i in range(self.obs_size ** 2, 2 * self.obs_size ** 2):
                    obs[i] = False  
                    
                for x,z in sheep_locations:
                    obs[self.obs_size ** 2 + math.floor(z) + math.floor(x) * self.obs_size] = True 
                    
                # Get wall locations
                grid = observations['floorAll']
                for i, x in enumerate(grid):
                    obs[2 * (self.obs_size ** 2) + i] = x == 'end_portal_frame'

                # Rotate observation with orientation of agent
                obs = obs.reshape((self.num_items_in_observation_array, self.obs_size, self.obs_size))
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
                self.facing_creeper = observations['LineOfSight']['type'] == 'Creeper'
                self.facing_creeper = observations['LineOfSight']['type'] == 'Sheep'
                self.facing_wall = observations['floorAll'][int((len(grid) ** 0.5) * ((len(grid) ** 0.5)//2-1) + (len(grid) ** 0.5)//2)] == 'end_portal_frame'
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
        plt.title('TheWalkingDead')
        plt.ylabel('Return')
        plt.xlabel('Steps')
        plt.savefig('returns.png')

        with open('returns.txt', 'w') as f:
            for step, value in zip(self.steps[1:], self.returns[1:]):
                f.write("{}\t{}\n".format(step, value))


if __name__ == '__main__':
    ray.init()
    trainer = ppo.PPOTrainer(env=TheWalkingDead, config={
        'env_config': {},           # No environment parameters to configure
        'framework': 'torch',       # Use pyotrch instead of tensorflow
        'num_gpus': 1,              # We aren't using GPUs
        'num_workers': 0            # We aren't using parallelism
    })

    # trainer.load_checkpoint("C:\\Users\\Owner\\Desktop\\Malmo\\Python_Examples\\checkpoint-36")
    i = 0
    while True:
        print(trainer.train())
        i += 1
        if i % 2 == 0:
            checkpoint = trainer.save_checkpoint(Path().absolute())
            print("checkpoint saved")
