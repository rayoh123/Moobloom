---
layout: default
title: Status
---
## Project Summary: 
The goal of our project is to train our agent to be adept at evading hostile mobs such as zombies, 
skeletons, and creepers while learning that passive mobs like cows, sheep, and pigs are safe. This is an
interesting thing to do because a common issue for Minecraft players is trying to avoid death via hostile mobs 
in their first few in-game nights. It will be interesting to see if an AI trained with reinforcement learning would 
be able to mimick the same escape strategies employed by human players.
## Approach: 
We are training the AI to escape from hostile mobs using reinforcement learning. Our hope is that 
the agent will eventually learn to maximixe the distance between itself and any hostile mobs. 
The update equation that we use in our project is: WRITE UPDATE EQUATION HERE. 

In our setup, we place the agent in the center of a flat, open field and randomly spawn hostile mobs like zombies on the field. The agent observes a 7 by 7
grid centered on it, and can see any entities in this grid. The agent can respond with one of three actions: turning left in place, 
turning right in place, or moving forward. 

Since we are training the agent to escape from hostile mobs, the goal is to stay alive for as long as possible. As such, the agent receives a positive reward for every 
gametick that it remains alive. Additionally, since taking damage is detrimental to the goal of escaping from mobs, the agent receives a negative reward
whenever it takes damage from a hostile mob. Therefore, the reward function that we use is: WRITE REWARD FUNCTION HERE.

## Evaluation:
We can evaluate our agent's performance quantitatively by comparing the agent's average reward near the beginning of its 
training to its average reward near the end of its training. If there is a noticable and significant increase in average 
reward, that is good. If there is no increase in average reward, that is bad. Here is a chart of the agent's average reward over time: 
INSERT CHART HERE. 

We can evaluate our agent's performance qualitatively by seeing if the agent takes a reasonable course of action when it is near a hostile mob. Namely, 
when the agent encounters a hostile mob, it should immediately turn and move in the opposite direction. If the agent moves perpendicular to the mob's 
path towards the agent, that is bad. Our agent BLAH BLAH.
INSERT GREEN CHECK MARK GOOD DIAGRAM AND RED X MARK BAD DIAGRAM.

## Remaining Goals and Challenges:
TBD

## Resources Used:
- [OpenAI Hide and Seek](https://www.youtube.com/watch?v=Lu56xVlZ40M). Our project will be similar to this interesting 
AI project, except less ambitious in scope. 
- [Fighting Zombies in Minecraft with RL Research Paper](http://cs229.stanford.edu/proj2016/report/UdagawaLeeNarasimhan-FightingZombiesInMinecraftWithDeepReinforcementLearning-report.pdf). 
This is an interesting explanation of how to do something slightly similar to what we are attempting.