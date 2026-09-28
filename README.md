# Steam Recommender 

## Overview
A web application built on the Python Django framework with the goal of providing video games suggestions from Steam tailored to a user's interest, based on data collected from their steam library.<br><br>
Personally, scrolling through the Steam store page is a bit lackluster, and most of the games are not even tailored to my interests of _roguelikes_ and _action_ based video games. To mitigate this mild annoyance, this application was developed, having a third party such as OpenAI to generate summaries based on recent game playtime and chat with it for additional suggestions regarding Steam games. Additionally, this does not have to tailored just to you, the application allows you to enter anybody's user id/persona name, so you can even generate suggestions for your friends, for example to gift them a game they have not played that still aligns with their interests.

## How it works
- 2 Steam-centered APIs that provide functions to easily parse user data (SteamDB, and SteamSpyPi)
- Open AI API, the core behind AI generated suggestions
- You enter a steam profile url, and you get redirected to a page that displays their entire library, including recently played games (within the last two weeks)
- You can generate summaries based on recent play time; top game genres and tags that are useful in finding other niche games that are still relevant
- Ask OpenAI via an integrated chat window for specific suggestions

## TODO
- Develop UI for chat window and create summaries, to be able to display the JSON data fetched from private endpoint

## Data collection/usage
- Data collected is solely data that is on Steam, which includes almost all games in a user's library (except for freebies), and Steam profile data for UI visuals
