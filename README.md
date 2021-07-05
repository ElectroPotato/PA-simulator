# PA-simulator
Simulation to determine the statistical chances of successfully capturing a ringleader unit in the Protocol Assimilation system within a single 28 day cycle.
* Simulator assumes optimal play as described by guide provided in this image. https://pbs.twimg.com/media/E5CzhbRXEAEB-XH.jpg
* Simulator also assumes perfect timing such that no time-gated or capped resources are wasted.
* nTrials: Edit this number to change the number of PA playthroughs to simulate
* Variables a-f: Starting conditions for the simulation, as described by in-text comments
* Uncomment matplotlib block to produce histograms for capture day and number of times the 3* unit appears on the field, requires module


## Notes:

* When provided very limited excess impulses and aid commission tickets, on average around 30% of users will capture the ringleader unit within a 28 day cycle, while 70% of users will see the 3* unit on the field at least once

## Meta-sim results
* 1 extra surplus impulse corresponds to approximately an additional 0.5% chance to capture the ringleader unit by the end of the cycle
* 1 extra Svarog aid commission corresponds to approximately an additional 1.3% chance to capture the ringleader unit by the end of the cycle
* Among users who capture the ringleader unit:
  * Increasing the number of aid commissions to use will decrease the average impulse expense to capture.
  * Increasing the number of extra impulses available for use has a very minor negative correlation with the average aid commission expense to capture, although this is negigible for low usage levels of both resources. 

## Long-term sim
* Simulate a number of players participating in the ProAss system across the specified number of banners
* JSON file used to set majority of parameters:
  * Provide a list of the number of capture resources that will be supplied each month
  * Declare each banner separately, providing the names, quantities, and rarities of units of interest, as well as assigning priority numbers and a desired amount to obtain from that banner under a blue sky scenario.
  * If the total number of units assigned in the banner does not reach 100, the banner will be backfilled with nameless mooks to ensure the proportion of rarities in the pool is correct.
  * Priority focus level to assign units of a particular priority level and higher to the objective pool, used to determine how to proceed through the banner and whether it is necessary to whale.
  * Desire limit to limit the maximum number of times a unit can exist in the objective pool, overriding desire counts assigned in the banners
  * Modifications will be required in order to collect metrics other than the ones selected
## Contact 
MashedPotato#3551 in discord.gg/gfen for inquiries
