# PA-simulator
Simulation to determine the statistical chances of successfully capturing a ringleader unit in the Protocol Assimilation system within a single 28 day cycle.
* Simulator assumes optimal play as described by guide provided in this image. https://pbs.twimg.com/media/E5CzhbRXEAEB-XH.jpg
* Simulator also assumes perfect timing such that no time-gated or capped resources are wasted.
* nTrials: Edit this number to change the number of PA playthroughs to simulate
* Variables a-f: Starting conditions for the simulation, as described by in-text comments
* Uncomment matplotlib block to produce histograms for capture day and number of times the 3* unit appears on the field, requires module


## Notes:

* On average, around 30% of users will capture the ringleader unit within a 28 day cycle, while 70% of users will see the 3* unit on the field at least once

## Meta-sim results
* 1 extra surplus impulse corresponds to approximately an additional 0.5% chance to capture the ringleader unit by the end of the cycle
* 1 extra Svarog aid commission corresponds to approximately an additional 1.3% chance to capture the ringleader unit by the end of the cycle
* Among users who capture the ringleader unit:
  * Increasing the number of aid commissions to use will decrease the average impulse expense to capture.
  * Increasing the number of extra impulses available for use has a very minor negative correlation with the average aid commission expense to capture, although this is negigible for low usage levels of both resources. 


## Contact 
MashedPotato#3551 in discord.gg/gfen for inquiries
