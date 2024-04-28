# GoniometerApplication

# The functionalities done
- Three file modes (maybe have to double check selection of files seemed weird during presentation. Maybe running just all files in order but couldn't double check)
- Calibration finding limits
- Running modes stop and pause
- Velocity varying working
- Checking for motor connection in some areas
- Initial offset just for position 
- An incorrectly done Axis Control Mode
- Logs and angle output set up for pitch

# The functionalities/fixes coming up
- Fix timing (Look at MotorSetup.py)
    - Look at past graphs the timing is off and its marked in MotorSetup.py where the problem lies
    - Either compensate for comp time or see if you can reduce the sleep thats currently there

- Add more motors
    - Adding more motors should not be too difficult just creating more object instances of the Motor class 
        - Motor class needs small edits for defining the usual set limits and such with it looking by serial connection to define them being different motors
    - Read more columns from the file to find more angle. With this there must be a quicker way to turn on all motors and move all motors at similar times by grouping these motor movements in a better way than set up
        - current set up will most likely make time delay between all different motors. At that point running the three motors on different threads to all run at once might be a method that could help. Nothing we worked on trying since we did the one motor but the motor rn and goes for the time frame so defining all moving and then that time frame can be looked at to see if threading is unneeded if the method of calling them one after the other is quick enough

- Fix offset to affect the rest of the file input (MotorSetup.py)
    - Currently just sets beginning position but was unsure if this should change the file input more directly
        - say off angle 6 then the new range would be 4 to -16 instead of -10 to 10 because of the 6 being a theoretical new 0 but should be easy to implement
    - Adding more offset inputs for the other angles

- Fix Axis Control Mode to run on run thread
    - Currently this is really not working. The biggest problem was making it work with the run thread 
    - Current set up doesn't check mode and doesn't need a mode to run it was just for potential presentation purposes

- Add more angle connection 
    - Currently the signaling is only set up to the one angle of pitch so setting up the other connections is needed 
    - Look at main.py lines 180-196 for copying that into all of the angles with the pitchEdit

- Lights on electrical box (Run Through Connection.py)
    - Lights on box is to tell when power is going to motor so more checking if the motor is active is needed through every part to help tell when the light should be on or off
    - Then messing around with the pyserial to the arduino. A lot of pass code from us doing that I got rid of but the Connection.py should show how to check ocnnection then its creating a definition for ser connection. It should more likely than not be a thing where you establish a connection when the event of on changes to change light on or off. Other option is a permanent connection but from what it seemed is there is a timeout part to it

- Adding odrive calibration to calibration (look at calibration to understand what must be done for odrive calibration )
    - odrive calibration can be done from odrive gui but would be nice to do from HMI but it will hit the limits if not done correctly so creating a physical of software method of running that calibration could help for a more efficient calibration


# General Recommendations

I would recommend looking at all files. They all have purpose comments on top of the file to tell about what they do. Then also looking at our past presentations and such explaining whats where and why. Mostly the parts talking about the main operations of the HMI. It is helpful to get an idea of what the plan was.

Frontend folder is all pyQT looks so all the .ui files and the css styling with a class for the logging and angles. Any references to these attributes will most likely be by their className defined in the .ui to help grab, link, or change aspects of those frontend elements. Backend has all the mode controlling with a separate folder for the motor driving. RunManager currently is a global instance with the big thing of only openeing that 1 instance that has objects of each motor that is remembered no matter what as long as the application does not close. Main.py has all of the functions of and run thread of the front end operations that connect to the mode runs. To add more motors you would just need to edit the motor class a bit to allow for custom limits for each motor and then flexing the csv reading for it. All motor and should be found with serial which can be put into the .env file for finding. Other more permanent vars should be put in there.

So the run thread is mean to just be used for the mode runs to allow for interaction with the HMI while there is a mode running. It is needed since they both take so much processing to run the modes and update the frontend with angle and logging. The thread splitting could also be a problem with computational time since there is more of a split in resources. The run thread is easy to use BUT WHENEVER you have a run stuck doing something make sure it has this line 

    QApplication.processEvents() 

to update the process beacuse if not frontend will crash if interacted with.

# Other files

The files outside of the Frontend and Backend like GenerateCSV and GraphResults help for running and setting up the csvs and the results.


# Additional information 

Besides that look more in the files if you can along with reading up on odrive and PyQt documentation. I was the main HMI developer for this project with interfacing with the motor so I am going to leave my discord username here for whoever is working on this later down the road around Septemeber. Will try to remember to add anyone I get around then. If you need to ask questions or just need general help I will be more than willing to and I am on discord often enough that I should hopefully get back to you quick. Just for reference, I had no idea about PyQt or even interfacing with motors before doing this project. All I had done was an unfinished website, app, and game in my software engineering classes so give it some time to learn everything especially since you are continuing the project from a different team. Number 1 advice is just ask questions and be okay with not knowing stuff at first. 

Discord: gorditochubs

My name is Justin in case you do end up needing help.