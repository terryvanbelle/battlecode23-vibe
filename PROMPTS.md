# PROMPTS

Every prompt the owner sends, verbatim, in order. Times are PDT (America/Los_Angeles). Prompts that a `/loop` fires
(for example "task check") are not recorded; the `/loop` command itself is (owner, prompts 4-5).

## 1. 2026-10-07 07:45 PDT

We are going to build a world-class champion Battlecode bot.  Battlecode is a contest where the contestants implement bots to play against other bots in an arena.  Each year’s rules are different from prior years, but they all share some common features.  We have built bots for several prior years already (Github repositories, in order of attempt:  battlecode22-vibe, battlecode26-vibe, battlecode25-vibe, battlecode21-vibe, battlecode20-vibe, and battlecode24-vibe.  Each attempt was built on previous attempts, so weight the findings of later projects higher than earlier ones).  Read through the code and documentation for these projects thoroughly to learn what has already been done, and what has worked or not worked.  Pay particular attention to files called RESEARCH.md, LEARNINGS.md, DESIGN.md, METHOD.md, and TRAINING_ALGORITHM.md.  Also review all code and documentation from the github repository anicolao/bcenv.  Feel free to steal any code that might be useful to you.  The repository battlecode-vibe has a file called ADVICE.md, storing cross-year advice that will be useful to you.  You’ll also find there files on basic principles, which will be useful, though please ignore any line tagged as matching the current year.

We’re not participating in an actual Battlecode tournament, we’re practicing.  In an actual tournament, you would have two sources of data:  local fights against old versions of yourself, and online scrimmages against a variety of opponents in the tournament standings.  We can’t perfectly replicate this latter source of data, but we should try to get as close as possible. 
Please do a thorough check of the web, especially github, for competitor bots from the relevant year that are publicly accessible.  Download all of them to serve as your benchmark.  You may not read their code, except to initially verify that they don’t pose any security risk, but you are encouraged to analyze their tactics in games.

Build a replica of the official Battlecode judging infrastructure using galaxy as a base.  You will use this infrastructure for your online scrimmages.  Enter your current competitor and the downloaded bots in the ladder and challenge bots slightly better and worse than you to scrimmages.  In the spare VM cycles, have random bots on the ladder do the same.  Ensure that none of this work has any effect on the official Battlecode infrastructure.

When you have thoroughly read all recommended repositories, formulate your own TRAINING_ALGORITHM.md file.  This file should be concise, complete, and formulated in year-agnostic terms.  Please do not simply copy a previous year’s TRAINING_ALGORITHM file.  You are forbidden from reading port-mortems from the current year.  Post-mortems from any other year are fair game.

You should start by building a strong, robust foundation in the basics:  good economy management; ensuring that your bots can move freely and efficiently to their destinations; board exploration; exploiting map symmetries; effective combat; and ensuring no bytecode overruns.  These basics are fundamental.  If you don’t have them right, nothing built on top of them will be effective.  Invest time at the beginning in building a good code architecture and good tools for understanding everything that happens in a game replay file.  Generate graphs that illustrate your progress, and keep them up to date.  Write comprehensive unit tests for the bot and all tooling, keep them up to date, and run them after every change.  

Make sure that your attempts are a good combination of incremental tweaks and big swings.  If you get stuck for ideas, review principles that have worked in other years.  There will be times when no attempts are successful for a long period.  At those times, it’s important to keep trying new things, and to not give up.  If you believe that a complete rewrite will help, then you should do so.  At no time should you stop and wait for me to give you a new idea.

Starting with this one, save all of my prompts in a document called PROMPTS.md.  Note that the user is in the PDT timezone.

This year we will compete in Battlecode 2023.  Store all results in a new Github repository called battlecode23-vibe.  Download the rules and begin.

## 2. 2026-10-07 07:47 PDT

/loop 30m task check

## 3. 2026-10-07 07:55 PDT

You can clear local storage from bc24 to free up disk space

## 4. 2026-10-07 08:20 PDT

To avoid clutter, don't store any of the /loop commands in PROMPTS

## 5. 2026-10-07 08:23 PDT

Sorry, what I meant was don't record any command in PROMPTS that was triggered by a /loop (e.g. "task check")

## 6. 2026-10-07 10:09 PDT

Keep going

## 7. 2026-10-07 11:20 PDT

What is the progress on the galaxy-based infrastructure?

## 8. 2026-10-07 11:25 PDT

Sounds good.  Ideally, once it's built, I'd like to have web access to the infrastructure so that I can see who's ranked where, and replay scrimmage games.  If that's not possible, then at least maintain screenshots of the most recent state in github so that I can consult them that way

## 9. 2026-10-07 13:11 PDT

Once the site is ready, please write a file with instructions on how to access it

## 10. 2026-10-07 15:00 PDT

Try again

## 11. 2026-10-07 16:09 PDT

I just tried the replica web server.  It looks great, but I'd really like you to use the exact same look and feel as the one in play.battlecode.org.  The main purpose of replicating galaxy is for you to get used to the actual contest interface, so I'd like you to be submitting bots, challenging opponents, and downloading the game results all from the replica.  This will be less efficient than you doing it yourself, but that's the point.  You need to get used to the actual contest environment, which is where you'll be getting all your ladder matches during the actual contest.

## 12. 2026-10-07 16:20 PDT

Remember that none of this should affect the real play.battlecode.org in any way

## 13. 2026-10-07 18:21 PDT

Because you will have access to many fewer ladder replays through the replica, you should make sure that each one counts when coming up with new ideas.  Instrument them to get as much information as possible per game

## 14. 2026-10-07 ~18:24 PDT

It looks like all of our games are Unranked, while games between two benchmark bots are Ranked.  Is that intentional?

## 15. 2026-10-07 ~18:27 PDT

This artificial limit on number of matches is going to be a problem.  I wanted realistic, but that seems a bit too realistic at this point.  Is there a setting to increase it?

## 16. 2026-10-07 18:30 PDT

That sounds good, do that

## 17. 2026-10-07 ~19:25 PDT

In a real tournament, what would be the optimal strategy for when to issue a ranked challenge vs. an unranked challenge?

## 18. 2026-10-07 19:33 PDT

OK, from now on I'd like you to use optimal strategy for deciding what kinds of games to challenge.  Make sure it's documented

## 19. 2026-10-08 05:45 PDT

Can you give me a summary of last night?

## 20. 2026-10-08 06:20 PDT

Can you tell me more about the panel?  What bots are on it?

## 21. 2026-10-08 06:25 PDT

How do we compare a candidate against g_iter0?  Do we submit the candidate, run the unranked games, and then swap g_iter0 back in?

## 22. 2026-10-08 06:30 PDT

How do you select candidates?  Do you do local head-to-head evaluations with g_iter0 first?

## 23. 2026-10-08 06:35 PDT

Yes, I think that's wise.  If you want to bring back the previous-year practice of building archetypes, that also seems like a good idea to me

## 24. 2026-10-08 06:50 PDT

I can't seem to find where on the replica I can view matches.  What am I missing?

## 25. 2026-10-08 06:58 PDT

Got it, thanks!

## 26. 2026-10-08 07:55 PDT

/loop 2h Make sure everything in the progress directory is up to date

## 27. 2026-10-08 08:45 PDT

Can you tell me more about how you encode information in the game replays?

## 28. 2026-10-08 09:15 PDT

Please report all times using PDT

## 29. 2026-10-08 09:50 PDT

The number of benchmark vs. benchmark games seems a bit excessive.  Now that we have a basic ordering, can we maybe restrict the number of those games so that we can fit more candidate vs. benchmark games in?

## 30. 2026-10-08 10:00 PDT

That sounds good to me.  I'm also OK if you want to restrict autoscrim to just the top N bots

## 31. 2026-10-08 10:05 PDT

While a candidate is being evaluated, I'd like you to continue working locally to improve the candidate, rather than pausing to wait for the results.  We can't let ourselves get blocked on waiting for scrimmages
