/*
    pixi-tools: a set of software to interface with the Raspberry Pi
    and PiXi-200 hardware
    Copyright (C) 2013, 2014, 2015 Astro Designs Ltd.

    pixi-tools is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
*/

#include <libpixi/pixi/simple.h>
#include <libpixi/util/command.h>
#include <libpixi/util/string.h>
#include <libpixi/pixi/spi.h>
#include <libpixi/util/io.h>

#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>
#include <math.h>

//#include "registers.h"

int pixi_gpio_setup(void);
int pixi_dalek_move(int direction, int speed, int time_ms);
int pixi_dalek_look(int start_alt, int start_az, int alt, int az, int inc);
void pixi_dalek_speak(int voice);
static int pixi_dalek_linefollow(int mode);


// Keyboard scanning stuff...
static void ttyRaw (int fd)
{
	struct termios term;
	int result = tcgetattr(fd, &term);
	if (result < 0)
		perror("tcgetattr");
	cfmakeraw (&term);
	result = tcsetattr(fd, TCSAFLUSH, &term);
	if (result < 0)
		perror("tcgetattr");
}

/// Disable line-buffering
/// This can screw up your terminal, use the 'reset' command to fix it.
static void ttyInputRaw (int fd)
{
	struct termios term;
	int result = tcgetattr(fd, &term);
	if (result < 0)
		perror("tcgetattr");
	term.c_lflag &= ~(ICANON | ECHO);
	result = tcsetattr(fd, TCSAFLUSH, &term);
	if (result < 0)
		perror("tcgetattr");
}

/// Enable line-buffering
static void ttyInputNormal (int fd)
{
	struct termios term;
	int result = tcgetattr(fd, &term);
	if (result < 0)
		perror("tcgetattr");
	term.c_lflag |= (ICANON | ECHO);
	result = tcsetattr(fd, TCSAFLUSH, &term);
	if (result < 0)
		perror("tcgetattr");
}

static const char keyUp[]    = {0x1b, 0x5b, 0x41, 0};
static const char keyDown[]  = {0x1b, 0x5b, 0x42, 0};
static const char keyRight[] = {0x1b, 0x5b, 0x43, 0};
static const char keyLeft[]  = {0x1b, 0x5b, 0x44, 0};



/*
 * Register access (for backward-compatibility)
 *********************************************************************************
 */
static int pixi_spi_set (int address, int data) {
   pixi_registerWrite (address, data);
   return 0;
}

static int pixi_spi_get (int address, int data) {
   return pixi_registerRead (address);
}


/*
 * dalek_configuration:
 *********************************************************************************
 */
int pixi_gpio_setup(void)
{
   // Setup GPIO1 mode (F4:Rover-5)
   // 0 =  Reserved
   // 1 =  Reserved
   // 2 =  basic GPIO (Input) Line detector
   // 3 =  basic GPIO (Input) Line detector
   // 4 =  basic GPIO (Input) Line detector
   // 5 =  basic GPIO (Input) Line detector
   // 6 =  basic GPIO (Input) Line detector
   // 7 =  basic GPIO (Input) Line detector
   // 8 =  basic GPIO (Input) Line detector
   // 9 =  basic GPIO (Input) Push-Button Switch (Start/Stop)
   // 10 = basic GPIO (Output) Voice Control(2)
   // 11 = basic GPIO (Output) Voice Control(3)
   // 12 = basic GPIO (Output) Voice Control(4)
   // 13 = basic GPIO (Output) Voice Control(5)
   // 14 = GPIO_f? (LEDS)
   // 15 = GPIO_f? (LEDS)
   // 16 = GPIO_f? (LEDS)
   // 17 = GPIO_f? (LEDS)
   // 18 = GPIO_f? (LEDS)
   // 19 = GPIO_f? (LEDS)
   // 20 = GPIO_f? (LEDS)
   // 21 = GPIO_f? (LEDS)
   // 22 = GPIO_f? (LEDS)
   // 23 = GPIO_f? (LEDS)
   pixi_spi_set(0x28, 0x0000);
   pixi_spi_set(0x29, 0x0000);
   pixi_spi_set(0x2a, 0x0000);
   pixi_spi_set(0x2b, 0x4411);
   pixi_spi_set(0x2c, 0x4444);
   pixi_spi_set(0x2d, 0x4444);

   // Setup GPIO2 mode (F5:Rover-5)
   // 0 =  basic GPIO (Motor power enable)
   // 1 =  basic GPIO (Camera Servo)
   // 2 =  basic GPIO 
   // 3 =  basic GPIO (Camera Servo)
   // 4 =  basic GPIO (Motor PWM)
   // 5 =  basic GPIO (Motor PWM)
   // 6 =  basic GPIO (Motor PWM)
   // 7 =  basic GPIO (Motor PWM)
   // 8 =  basic GPIO (Buzzer)
   // 9 =  basic GPIO (Headlamp Off)
   // 10 = basic GPIO
   // 11 = basic GPIO (Headlamp Off)
   // 12 = basic GPIO (Motor Dir)
   // 13 = basic GPIO (Motor Dir)
   // 14 = basic GPIO (Motor Dir)
   // 15 = basic GPIO (Motor Dir)
   pixi_spi_set(0x2e, 0x2222);
   pixi_spi_set(0x2f, 0x4444);
   pixi_spi_set(0x30, 0x4444);
   pixi_spi_set(0x31, 0x4444);

      // Setup GPIO3 mode
   // 0 =  GPIO2 mode (Output)
   // 1 =  GPIO2 mode (LCD/VFD)
   // 2 =  GPIO2 mode (Output)
   // 3 =  GPIO2 mode (LCD/VFD)
   // 4 =  GPIO2 mode (Output)
   // 5 =  GPIO2 mode (LCD/VFD)
   // 6 =  GPIO2 mode (Output)
   // 7 =  GPIO2 mode (LCD/VFD)
   // 8 =  GPIO2 mode (Output)
   // 9 =  GPIO2 mode (LCD/VFD)
   // 10 = GPIO2 mode (LCD/VFD)
   // 11 = GPIO2 mode (LCD/VFD)
   // 12 = basic GPIO
   // 13 = basic GPIO
   // 14 = PWM Input (basic input)
   // 15 = PWM Input (basic input)
   pixi_spi_set(0x32, 0x1111);
   pixi_spi_set(0x33, 0x1111);
   pixi_spi_set(0x34, 0x1111);
   pixi_spi_set(0x35, 0x1111);

   // Initialise all I/O
   pixi_spi_set(0x20, 0); // GPIO1 (not used)
   pixi_spi_set(0x21, 0); // GPIO1 (direct I/O not used)
   pixi_spi_set(0x22, 0); // GPIO1 (direct I/O not used)
   pixi_spi_set(0x23, 0); // GPIO2 (motor power off)
   pixi_spi_set(0x24, 0); // GPIO2 (headlamps off)
   pixi_spi_set(0x25, 0); // GPIO3 (direct I/O not used)
   pixi_spi_set(0x26, 0); // GPIO3 (direct I/O not used)
   
   pixi_spi_set(0x40, 75); // Camera pan
   pixi_spi_set(0x41, 75); // Camera tilt
   pixi_spi_set(0x44, 0); // Motor off
   pixi_spi_set(0x45, 0); // Motor off
   pixi_spi_set(0x46, 0); // Motor off
   pixi_spi_set(0x47, 0); // Motor off
   pixi_spi_set(0x4F, 0); // Direct PWM control

   // PWM Frequency
   pixi_spi_set(0x7a, 0x500); // 50Hz (need to check...)

   return(0);
}

	
/*
 * dalek_look:
 *********************************************************************************
 */
int pixi_dalek_move(int direction, int speed, int time_ms)
{

   if ((time_ms < 10000) && (time_ms >= 0)) {
      switch (direction) {
      case 5 : //stop
         printf("Move: Stop [speed = %d, time = %dms\n", speed, time_ms);
         pixi_spi_set(0x44, 0x0000);    // FR
         pixi_spi_set(0x45, 0x0000);    // FL
         pixi_spi_set(0x46, 0x0000);    // BR
         pixi_spi_set(0x47, 0x0000);    // BL
         break;
      case 8 : //forwards
         printf("Move: Forwards [speed = %d, time = %dms\n", speed, time_ms);
         pixi_spi_set(0x44, speed);    // FR
         pixi_spi_set(0x45, speed);    // FL
         pixi_spi_set(0x46, 0x0000);    // BR
         pixi_spi_set(0x47, 0x0000);    // BL
         break;
      case 2 : //backwards
         printf("Move: Backwards [speed = %d, time = %dms\n", speed, time_ms);
         pixi_spi_set(0x44, 0x0000);    // FR
         pixi_spi_set(0x45, 0x0000);    // FL
         pixi_spi_set(0x46, speed);    // BR
         pixi_spi_set(0x47, speed);    // BL
         break;
      case 4 : // left
         printf("Move: Left [speed = %d, time = %dms\n", speed, time_ms);
         pixi_spi_set(0x44, speed);    // FR
         pixi_spi_set(0x45, 0x0000);    // FL
         pixi_spi_set(0x46, 0x0000);    // BR
         pixi_spi_set(0x47, speed);    // BL
         break;
      case 6 : // right
         printf("Move: Right [speed = %d, time = %dms\n", speed, time_ms);
         pixi_spi_set(0x44, 0x0000);    // FR
         pixi_spi_set(0x45, speed);    // FL
         pixi_spi_set(0x46, speed);    // BR
         pixi_spi_set(0x47, 0x0000);    // BL
         break;
      default : // unsupported command
         printf("Move: Unsupported command\n");
         break;
      }

      usleep (1000 * time_ms);      
      pixi_spi_set(0x44, 0x0000);    // FR
      pixi_spi_set(0x45, 0x0000);    // FL
      pixi_spi_set(0x46, 0x0000);    // BR
      pixi_spi_set(0x47, 0x0000);    // BL
   }
   return(0);
}


/*
 * dalek_look:
 *********************************************************************************
 */
int pixi_dalek_look(int start_alt, int start_az, int alt, int az, int inc)
{
   int current_alt;
   int current_az;
   const float gain = 31;
   const float offset = 76.5;

   printf("Look: [Alt = %d, Az = %d, rate = %d\n", alt, az, inc);

   if (start_az == 0)
      start_az = (((pixi_spi_get(0x43, 0) & 1023)-offset)/gain)*90.0;
   if (az < start_az) {
      for (current_az = start_az; current_az > az; current_az = current_az - inc) {
         pixi_spi_set(0x43, (int)(((current_az/90.0)*gain)+offset));
         usleep (20000); } }
   if (az > start_az) {
      for (current_az = start_az; current_az < az; current_az = current_az + inc) {
         pixi_spi_set(0x43, (int)(((current_az/90.0)*gain)+offset));
         usleep (20000); } }

   if (start_alt == 0)
      start_alt = ((102 - (pixi_spi_get(0x41, 0) & 1023))/gain)*90;
   if (alt < start_alt) {
      for (current_alt = start_alt; current_alt > alt; current_alt = current_alt - inc) {
	     pixi_spi_set(0x41, (102-(int)((current_alt/90.0)*gain)));
         usleep (20000); } }
   else {
      for (current_alt = start_alt; current_alt < alt; current_alt = current_alt + inc) {
	     pixi_spi_set(0x41, (102-(int)((current_alt/90.0)*gain)));
         usleep (20000); } }

   return(0);
}


/*
 * Dalek Speak:
 *********************************************************************************
 */
void pixi_dalek_speak(int voice)
{

   printf("Dalek speak... (%d)\n", voice);

   // Reset
   pixi_spi_set(0x25, 0); // GPIO3 (direct I/O not used)
   pixi_spi_set(0x26, 0); // GPIO3 (direct I/O not used)

   usleep(200000);

   switch(voice) {
      case 1 :
         // Exterminate
         printf("Say 'Exterminate!'\n");
         pixi_spi_set(0x25, 0x00);
         pixi_spi_set(0x26, 0x04);
         break;
      case 2 :
         // 
         printf("Say Voice #2\n");
         pixi_spi_set(0x25, 0x01);
         pixi_spi_set(0x26, 0x00);
         break;
      case 3 :
         // 
         printf("Say Voice #3\n");
         pixi_spi_set(0x25, 0x04);
         pixi_spi_set(0x26, 0x00);
         break;
      case 4 :
         // 
         printf("Say Voice #4\n");
         pixi_spi_set(0x25, 0x10);
         pixi_spi_set(0x26, 0x00);
         break;
      case 5 :
         // 
         printf("Say Voice #5\n");
         pixi_spi_set(0x25, 0x40);
         pixi_spi_set(0x26, 0x00);
         break;
      }
   
   usleep(200000);

   // Reset
   pixi_spi_set(0x25, 0); // GPIO3 (direct I/O not used)
   pixi_spi_set(0x26, 0); // GPIO3 (direct I/O not used)

}


/*
 * Dalek Line Follower:
 *********************************************************************************
 */
int pixi_dalek_linefollow(int mode)
{
	int speed_100 = 0x3ff; // full speed
	int speed_50 = 0; //0x1ff; // half speed
	int stalk_0lr = 75;
	int stalk_45l = 65;
	int stalk_45r = 85;
	int stalk_90l = 55;
	int stalk_90r = 95;
	int stalk_0alt = 50;
	int stalk_45alt = 75;
//	int stalk_90alt = 95;
	int finished = 0;
	int line_sense = 0;
	enum t_line_state {paper_LookingForRightOfLine, line_LookingForLeftOfLine, paper_LookingForLeftOfLine, line_LookingForRightOfLine} line_state = paper_LookingForRightOfLine;
	ttyInputRaw (STDIN_FILENO);

   printf("Dalek Line Follower/nVersion 1.0 build 26/10/15b \n");

	printf("press 'q' to quit\n");
 
   // Initialise GPIO & turn motors on
   pixi_gpio_setup();
   pixi_spi_set(0x37, 0);
   
   while (finished == 0) { // Loop continuously unless button pressed for > 5s

      printf("Press the button to start...\n");
      // Wait for start instruction
      while (((pixi_spi_get(0x21, 0) & 0x0004) == 0) && // Dalek button is pressed
             ((pixi_spi_get(0x3a, 0) & 0x0004) == 0) && // On-board switch is pressed
             (mode != 3)) {                             // Mode = 3
      }

      printf("Starting...\n");

      pixi_spi_set(0x43, stalk_0lr); // Eye-stalk azimuth
      pixi_spi_set(0x41, stalk_0alt); // Eye-stalk altitude

      usleep(5000000); // Delay here helps de-bounce switch

      pixi_dalek_speak(5);
      
      while (finished == 0) {
      
         // Look for a stop instruction...
         if (((pixi_spi_get(0x21, 0) & 0x0004) > 0) || // GPIO1(7) (Dalek Button)
             ((pixi_spi_get(0x3a, 0) & 0x0004) > 0) || // on-board switch
             ((pixi_spi_get(0x07, 0) & 0x0001) > 0)) { // GPIO1(7) (Test register bit(0))
            printf("Stopping...\n");
            pixi_dalek_move(5, 0, 0);
            finished = 1;
         }
         else if (mode == 0) {

            // Method 1: Simple oscillating action using a single sensor
            switch (line_state) {
	           case paper_LookingForRightOfLine: // Turning left
                  printf("State: paper_LookingForRightOfLine\n");
	               pixi_spi_set(0x44, speed_100);    // FR
                  pixi_spi_set(0x45, speed_50);    // FL
                  pixi_spi_set(0x46, 0x0000);    // BR
                  pixi_spi_set(0x47, 0x0000);    // BL
	              if ((pixi_spi_get(0x20, 0) & 0x0008) < 1) {
	                 line_state = line_LookingForLeftOfLine;
                         pixi_spi_set(0x36, 3); }
	              break;
	           case (line_LookingForLeftOfLine): // Turning left
                  printf("State: line_LookingForLeftOfLine\n");
                  pixi_spi_set(0x44, speed_100);    // FR
                  pixi_spi_set(0x45, speed_50);    // FL
                  pixi_spi_set(0x46, 0x0000);    // BR
                  pixi_spi_set(0x47, 0x0000);    // BL
	              if ((pixi_spi_get(0x20, 0) & 0x0008) > 1) {
	                 line_state = paper_LookingForLeftOfLine;
                         pixi_spi_set(0x36, 0); }
	              break;
	           case (paper_LookingForLeftOfLine): // Turning right
                  printf("State: paper_LookingForLeftOfLine\n");
                  pixi_spi_set(0x44, speed_50);    // FR
                  pixi_spi_set(0x45, speed_100);    // FL
                  pixi_spi_set(0x46, 0x0000);    // BR
                  pixi_spi_set(0x47, 0x0000);    // BL
	              if ((pixi_spi_get(0x20, 0) & 0x0008) < 1) {
	                 line_state = line_LookingForRightOfLine;
                         pixi_spi_set(0x36, 3); }
	              break;
	           case (line_LookingForRightOfLine): // Turning right
                  printf("State: line_LookingForRightOfLine\n");
                  pixi_spi_set(0x44, speed_50);    // FR
                  pixi_spi_set(0x45, speed_100);    // FL
                  pixi_spi_set(0x46, 0x0000);    // BR
                  pixi_spi_set(0x47, 0x0000);    // BL
	              if ((pixi_spi_get(0x20, 0) & 0x0008) > 1) {
	                 line_state = paper_LookingForRightOfLine;
                         pixi_spi_set(0x36, 0); }
	              break;
            }	            
            
         }
         else {
            // Method 2: Using an array of seven sensors to detect the actual line position
            line_sense = pixi_spi_get(0x20, 0) ^ 0x0F8; // 5-element sensor
            line_sense = line_sense & 0x0F8;
            
            // 00001 = 0x0008 = right 50, left -50, 
            // 00010 = 0x0010 = right 100, left 50, 
            // 00100 = 0x0020 = straight, full
            // 01000 = 0x0040 = left 100, right 50, 
            // 10000 = 0x0080 = left 50, right -50, 

            switch (line_sense) {
               case 0x0020: // Forward
                  printf("00100 / %04x\n", line_sense);
                  pixi_spi_set(0x44, speed_100);    // FR
                  pixi_spi_set(0x45, speed_100);    // FL
                  pixi_spi_set(0x46, 0x0000);    // BR
                  pixi_spi_set(0x47, 0x0000);    // BL
                  pixi_spi_set(0x43, stalk_0lr); // Turn head
                  break;
              case (0x0010): // Left a bit
              //case (0x0040): // Left a bit
                  printf("01000 / %04x\n", line_sense);
                  pixi_spi_set(0x44, speed_100);    // FR
                  pixi_spi_set(0x45, speed_50);    // FL
                  pixi_spi_set(0x46, 0x0000);    // BR
                  pixi_spi_set(0x47, 0x0000);    // BL
                  pixi_spi_set(0x43, stalk_45l); // Turn head
                  break;
              case (0x0040): // Right a bit
              //case (0x0010): // Right a bit
                  printf("00010 / %04x\n", line_sense);
                  pixi_spi_set(0x44, speed_50);    // FR
                  pixi_spi_set(0x45, speed_100);    // FL
                  pixi_spi_set(0x46, 0x0000);    // BR
                  pixi_spi_set(0x47, 0x0000);    // BL
                  pixi_spi_set(0x43, stalk_45r); // Turn head
                  break;
              case (0x0008): // Left a lot
              //case (0x0080): // Left a lot
                  printf("10000 / %04x\n", line_sense);
                  pixi_spi_set(0x44, speed_100);    // FR
                  pixi_spi_set(0x45, 0x0000);    // FL
                  pixi_spi_set(0x46, 0x0000);    // BR
                  pixi_spi_set(0x47, speed_100);    // BL
                  pixi_spi_set(0x43, stalk_90l); // Turn head
                  break;
              case (0x0080): // Right a lot
              //case (0x0008): // Right a lot
                  printf("00001 / %04x\n", line_sense);
                  pixi_spi_set(0x44, 0x0000);    // FR
                  pixi_spi_set(0x45, speed_100);    // FL
                  pixi_spi_set(0x46, speed_100);    // BR
                  pixi_spi_set(0x47, 0x0000);    // BL
                  pixi_spi_set(0x43, stalk_90r); // Turn head
                  break;
              
            }            
         }
      }
      usleep(1000000); // Delay here helps de-bounce switch
      finished = 0;
      // Look to see if the switch has been pressed for > 5s, exit program if it has...
      if (((pixi_spi_get(0x21, 0) & 0x0004) > 0) || // GPIO1(7) (Dalek Button)
          ((pixi_spi_get(0x3a, 0) & 0x0004) > 0) || // on-board switch
          ((pixi_spi_get(0x07, 0) & 0x0001) > 0) || // GPIO1(7) (Test register bit(0))
          (mode == 3)) {                            // Stop regardless if mode = 3!
         printf("Exiting line follower program...\n");

         pixi_spi_set(0x44, 0x0000);    // FR
         pixi_spi_set(0x45, 0x0000);    // FL
         pixi_spi_set(0x46, 0x0000);    // BR
         pixi_spi_set(0x47, 0x0000);    // BL
         pixi_spi_set(0x43, stalk_0lr); // Eye-stalk azimuth
         pixi_spi_set(0x41, stalk_45alt); // Eye-stalk altitude

         pixi_dalek_speak(1);  // Exterminate!

         finished = 1;
      }
   }

   ttyInputNormal (STDIN_FILENO);

   return(0);
}	

static int dalekConfigFn (const Command* command, uint argc, char*const*const argv)
{
	if (argc != 1)
   {
      return commandUsageError (command); }
   else {
      pixiOpenOrDie();
      pixi_gpio_setup();
      return 0;
   }

}

static Command dalekConfigCmd =
{
	.name        = "dalek-config",
	.description = "Configures PiXi GPIO",
	.function    = dalekConfigFn
};

static int dalekLineFollowFn (const Command* command, uint argc, char*const*const argv)
{
	int mode;
	
	if (argc != 2)
   {
      return commandUsageError (command); }
   else {
      mode = atoi(argv[1]);
      pixiOpenOrDie();
      usleep(1000000);
      pixi_dalek_linefollow(mode);
      return 0;
   }

}

static Command dalekLineFollowCmd =
{
	.name        = "dalek-linefollower",
	.description = "Enables the Line-Following mode...",
	.function    = dalekLineFollowFn
};

static int dalekSpeakFn (const Command* command, uint argc, char*const*const argv)
{
	int voice;
	
	if (argc != 2)
   {
      return commandUsageError (command); }
   else {
      voice = atoi(argv[1]);
      
      printf("Speak: Voice %d\n", voice);
   
      pixiOpenOrDie();
      pixi_dalek_speak(voice);
      return 0;
   }

}

static Command dalekSpeakCmd =
{
	.name        = "dalek-speak",
	.description = "Tells the Dalek to speak...",
	.function    = dalekSpeakFn
};

static int dalekForwardsFn (const Command* command, uint argc, char*const*const argv)
{
	int time_ms;
	
	if (argc != 2)
   {
      return commandUsageError (command); }
   else {
      time_ms = atoi(argv[1]);
      printf("Move: Forwards...\n");
   
      pixiOpenOrDie();
      pixi_dalek_move(8, 0x3ff, time_ms);
      return 0;
   }

}

static Command dalekForwardsCmd =
{
	.name        = "dalek-forwards",
	.description = "Tells the Dalek to move forwards...",
	.function    = dalekForwardsFn
};

static int dalekBackwardsFn (const Command* command, uint argc, char*const*const argv)
{
	int time_ms;
	
	if (argc != 2)
   {
      return commandUsageError (command); }
   else {
      time_ms = atoi(argv[1]);
      printf("Move: Backwards...\n");
   
      pixiOpenOrDie();
      pixi_dalek_move(2, 0x3ff, time_ms);
      return 0;
   }

}

static Command dalekBackwardsCmd =
{
	.name        = "dalek-backwards",
	.description = "Tells the Dalek to move backwards...",
	.function    = dalekBackwardsFn
};

static int dalekLeftFn (const Command* command, uint argc, char*const*const argv)
{
	int time_ms;
	
	if (argc != 2)
   {
      return commandUsageError (command); }
   else {
      time_ms = atoi(argv[1]);
      printf("Move: Left...\n");
   
      pixiOpenOrDie();
      pixi_dalek_move(4, 0x3ff, time_ms);
      return 0;
   }

}

static Command dalekLeftCmd =
{
	.name        = "dalek-left",
	.description = "Tells the Dalek to turn left...",
	.function    = dalekLeftFn
};

static int dalekRightFn (const Command* command, uint argc, char*const*const argv)
{
	int time_ms;
	
	if (argc != 2)
   {
      return commandUsageError (command); }
   else {
      time_ms = atoi(argv[1]);
      printf("Move: Right...\n");
   
      pixiOpenOrDie();
      pixi_dalek_move(6, 0x3ff, time_ms);
      return 0;
   }

}

static Command dalekRightCmd =
{
	.name        = "dalek-right",
	.description = "Tells the Dalek to turn right...",
	.function    = dalekRightFn
};

static int dalekLookForwardsFn (const Command* command, uint argc, char*const*const argv)
{
	
	if (argc != 1)
   {
      return commandUsageError (command); }
   else {
      printf("Look: Forwards...\n");
   
      pixiOpenOrDie();
      pixi_dalek_look(0, 0, 0, 0, 5);
      return 0;
   }

}

static Command dalekLookForwardsCmd =
{
	.name        = "dalek-look-forwards",
	.description = "Tells the Dalek to look forwards...",
	.function    = dalekLookForwardsFn
};

static int dalekLookLeftFn (const Command* command, uint argc, char*const*const argv)
{
	if (argc != 1)
   {
      return commandUsageError (command); }
   else {
      printf("Look: Left...\n");
   
      pixiOpenOrDie();
      pixi_dalek_look(0, 0, 0, 90, 5);
      return 0;
   }

}

static Command dalekLookLeftCmd =
{
	.name        = "dalek-look-left",
	.description = "Tells the Dalek to look left...",
	.function    = dalekLookLeftFn
};

static int dalekLookRightFn (const Command* command, uint argc, char*const*const argv)
{
	if (argc != 1)
   {
      return commandUsageError (command); }
   else {
      printf("Look: Right...\n");
   
      pixiOpenOrDie();
      pixi_dalek_look(0, 0, 0, -90, 5);
      return 0;
   }

}

static Command dalekLookRightCmd =
{
	.name        = "dalek-look-right",
	.description = "Tells the Dalek to look right...",
	.function    = dalekLookRightFn
};

static int dalekLookUpFn (const Command* command, uint argc, char*const*const argv)
{
	if (argc != 1)
   {
      return commandUsageError (command); }
   else {
      printf("Look: Up...\n");

      pixiOpenOrDie();
      pixi_dalek_look(0, 0, 90, 0, 5);
      return 0;
   }

}

static Command dalekLookUpCmd =
{
	.name        = "dalek-look-up",
	.description = "Tells the Dalek to look up...",
   .usage       = "usage: %s",
	.function    = dalekLookUpFn
};

static const Command* commands[] =
{
	&dalekConfigCmd,
	&dalekLineFollowCmd,
	&dalekSpeakCmd,
	&dalekForwardsCmd,
	&dalekBackwardsCmd,
	&dalekLeftCmd,
	&dalekRightCmd,
	&dalekLookForwardsCmd,
	&dalekLookLeftCmd,
	&dalekLookRightCmd,
	&dalekLookUpCmd
};

static CommandGroup dalekGroup = // <<<<< Enter name for this CommandGroup here... eg testGroup
{
	.name      = "dalek", // <<<<< Enter name for this group of functions / commands...
	.count     = ARRAY_COUNT(commands),
	.commands  = commands,
	.nextGroup = NULL
};

static void LIBPIXI_COMMAND_GROUP (10002) initGroup (void)
{
	addCommandGroup (&dalekGroup); // <<<<< Enter name for this CommandGroup here... eg &testGroup
}
