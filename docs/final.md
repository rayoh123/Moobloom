---
layout: default
title: Final
---
## VIDEO:

## PROJECT SUMMARY: 

The goal of our project is to train our agent to be adept at evading hostile mobs such as zombies, skeletons, and creepers while learning that passive mobs like cows, sheep, and pigs are safe. This is an interesting thing to do because a common issue for Minecraft players is trying to avoid death via hostile mobs in their first few in-game nights. It will be interesting to see if an AI trained with reinforcement learning would be able to mimick the same escape strategies employed by human players.
Our project as of now has an agent in an eclosed room with 2 zombies, 2 creepers and 3 sheeps. The enclosed room has a row of diamond blocks. If the agent reaches any block in this row, the agent wins and gets a reward for the same. The enclosed room also has a path towards the diamond blocks of least resistance i.e devoid of hostile mobs. The agent detects the best path to reach the diamond blocks and escapes the hostile.  

## APPROACH: 
__Baseline__: Our baseline for this project was for an agent to escape a single zombie on an open field. Our agent successfully did this 
by consistently running away from its spawn point in a straight line. While this was a success, it didn't show any complex behavior.
To surpass this baseline, our agent would have to be confined in an enclosed space and made to demonstrate some player-like 
intelligent actions to evade hostile mobs. In addition, its task would be made harder by the addition of multiple zombies and 
creepers. 
INSERT GIF OF AGENT SANITY CHECK FROM STATUS REPORT
__Approach&nbsp;#1__: First, our agent was placed in an enclosed room with no special characteristics.
__Approach&nbsp;#2__: Once our first approach yielded desirable results, we decided to make the environment slightly more interesting
by elongating the field into a football-field-like rectangle, where the agent spawns at one end of the field, the hostile mobs spawn 
in the middle, and a "touchdown" line of diamond blocks lie at the opposite end of the field. When the agent reaches the diamond blocks, 
it receives a huge positive reward and the mission immediately ends. This change was motivated by our realization that players often 
make temporary shelters for their initial nights in Minecraft. And when players are caught outside at night, they have to return to it 
without getting killed. Here, our diamond blocks are analogous to that safety zone.
__Approach&nbsp;#3__: Finally, out of curiosity, we decided to see if the agent would be able to detect paths of least resistance 
towards the diamond blocks. For example, if there was a completely safe tunnel that was devoid of hostile mobs leading towards the diamond 
blocks, would the agent eventually realize that this was the best path to take? In Minecraft gameplay, this would be analogous to taking 
a well-lit path towards one's base instead of a dark one filled with hostile mobs.


## EVALUATION: 
### Qualitative 
A good way to evaluate the performance of the agent is to judge how human its strategic decision-making is. For each of our approaches, we 
will see how similarly the actions taken by the agent resemble actions that would be taken by human players if they were placed in the 
same situations.
__Approach&nbsp;#1__: 
INSERT DRAWN PIC OF SETUP FOR CLOSED ROOM APPROACH
For the situation in which the agent is stuck in an enclosed room, a human would absolutely not want to stand in the center, where it would 
attract the maximal amount of hostile mobs. Instead, a human would stick close to the walls, where only 180 degrees of its body is exposed. 
This is what the agent does in this situation. As we can see in the demonstration below, the agent sticks close to the walls and 
continuously circles around the field. This allows it to lead the mobs on a wild goose chase in a circle. 

INSERT GIF HERE
__Approach&nbsp;#2__:
__Approach&nbsp;#3__:
### Quantitative
__Approach#1__:
We have created multiple graphs to better visualize the agent's improvement. First, we have a 
comprehensive rewards graph, which details the reward that the agent gets over time. 
INSERT REWARDS GRAPH HERE
As we can see, the graph shows that the agent's ability to obtain a higher reward improves over time. At first, the agent 
moves around the field randomly, which leads to a SOMETHING reward. However, as it trains, it is able to reach a much-higher 
SOMETHING reward. But in order to see how the agent is improving in more detail, we will also look at the damage that the agent takes over time from 
hostile mobs. 
INSERT DAMAGE TAKEN GRAPH HERE

INSERT 

__Approach&nbsp;#2__:
__Approach&nbsp;#3__:


## REFERENCES:




















