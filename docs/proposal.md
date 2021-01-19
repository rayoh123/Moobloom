---
layout: default
title:  PROPOSAL
---

## Summary of the Project
Problem Setup/Goal: A common problem for players in Minecraft is when they are outside at nighttime 
and they have to avoid dying to hostile animals. If a player is unarmed, the only solution is to run. 
However, many new players have difficulties evading hostile animals. Our AI agent should learn to 
survive at night time by avoiding different kinds of hostile animals, while determining that friendly 
animals are safe to walk by. (e.g. the agent should learn to stay further away from animals that 
shoot arrows than animals that require direct contact to harm, whereas animals like cows and pigs 
are not a concern).
Input/Output Semantics: The input that the agent will take is a 20x20 field on which both friendly 
and hostile animals are standing. The agent will determine a path to take through these animals 
which will allow it to survive the maximum amount of time.
Applications: This agent can be used to help players survive the nighttime.

## AI/ML Algorithms
In this project, we will use a cognitive model under reinforcement learning to train the AI agent.

## Evaluation Plan
We will quantitatively evaluate primarily based on the time that our agent survives. 
We will set specific benchmarks for how long they are able to do so, for example 30 
seconds, 60 seconds, 90 seconds, etc. After actually starting, we will have a more 
accurate idea of what times can be reasonably expected for different settings of the 
world (size of field, number of enemies, etc). With random walking and sprinting as 
the baseline, the agent should only survive for a few seconds. Our trained agent 
should be able to survive for many times that duration (maybe a few minutes?) when 
given the same input.

We can qualitatively test that our project is working correctly by observing and 
ensuring that the agent is running away from enemies and not running away from 
non-enemies. A sanity check is that with 1 enemy animal, the agent should be 
basically running away from it the entire time, and - assuming the enemy is not 
faster than the agent - should be able to avoid getting caught and survive forever. 
Any case with 1 enemy animal with additional non-enemy/friendly animals should behave 
identically to the case with only 1 enemy animal. 
 
A moonshot case is that with 10 zombies, 10 skeletons, and 10 creepers on a 
20x20 block field, the agent will survive for an hour.


## Appointment with the Instructor
Thursday (January 21, 2021) - 12:30 pm
