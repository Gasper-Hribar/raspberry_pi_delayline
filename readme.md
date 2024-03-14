# Delayline app for Raspberry Pi

This app allows the user to set a programmable delay via SPI communication with programmable delay chips such as SY89297U and MC100EP195B. The delay can be set for two independed channels.

The SY89297U chip can delay signals between 2 and 7 ns with 5 ps steps. Max setting in app is 5 ns as it assummes the 2 ns as default.

The SY100EP195B chip can delay two signals between 2,07 and 10,75 ns with approximately 8,5 ps steps. Max setting in app is 8695 ps or 8 ns as it assumes the 2,07 ns delay as default 0.

## Known issues:

Many.

## Updating the app

App update is available via checking the github repository. If the local branch is behind in commits, the prompt will ask the user if it should update the app. If answered 'yes', the 
updateService will pull the repository and restarted the app. 