// This is the main LED 8x8x8 cube code
// Created 6/4/19
// Created by Dominik Chraca
/*
 * SD card attached to SPI bus as follows:
 ** MOSI - pin 11
 ** MISO - pin 12
 ** CLK - pin 13
 ** CS - pin 10 (for MKRZero SD: SDCARD_SS_PIN)
*/

#include <SPI.h>
#include <SD.h>
#include <StopWatch.h>
//#include <MemoryFree.h>

//Versetile constants in ms
const byte button_speed = 70;
byte amount_variations = 4;

const byte pwm_res = 8; 

//For stopwatches
StopWatch right_button_watch;
StopWatch fps_watch;

const byte chipSelect = 10;
bool sd_ready = 0;
File dataFile;
const byte files_amount = 2; // This variable changes the amount of files that can be read from the SD card, max is 200
byte cube_files_amount = 0;
char cube_files[files_amount][13]; //[files_amount][char size]
byte cube_files_size[files_amount];// [files_amount]
bool run_once = 1;

// pins
#define data_out 9
#define r_button A1
#define l_button A0
#define analog_pin A2

byte anamation_pos = 4;
byte pwm_pos = 0;

int FPS_LOCATION[3] = {0,0,0};// xyz

//Variation 2 global variable---- this variable indicates if in var 2, look at print_frame function for the difference
bool var_2_par = 0;

void setup() 
{
 // For SD card
  pinMode(chipSelect,OUTPUT);
  
  randomSeed(analogRead(analog_pin));
  //For stopwatches
  right_button_watch.start();
  fps_watch.start();
  
  // Direct register manipulation is used for speed
  DDRD = B11111111;  // sets Arduino pins 0 to 7 as outputs.
  DDRB = DDRB | B00000011; // outputs on 8,9
  DDRC = DDRC | B00111000; // outputs on A3,A4,A5
  pinMode(r_button, INPUT);
  pinMode(l_button, INPUT);
  //Serial.println("Setup Done");
}

void loop() 
{
  byte LED[8][8][8]; // [z][y][x][value] < pwm res
  variation_zero(LED); // reset
  while (1)
  {
    //Serial.println("Running");
    //Buttons
    int fps = map(analogRead(analog_pin),0,1023,15,1000); // changes to ms
    if (digitalRead(r_button))
    {
      //Serial.println("Right button pressed");
      if (right_button_watch.ms() > button_speed)
      {
        variation_zero(LED); // resets
        ++anamation_pos;
        //Serial.println("Anamation shifted");
      }
      right_button_watch.restart();
    }
    if (digitalRead(l_button)and 0 and anamation_pos > 0)
    {
      if (right_button_watch.ms() > button_speed)
      {
        variation_zero(LED); // resets
        --anamation_pos;
      }
      right_button_watch.restart();
    }
    //Serial.print("POSITION: ");
    //Serial.println(anamation_pos);
    // Variations 
    if (anamation_pos == 0) // resets the entire array
    {
     variation_zero(LED); // resets
    }
    else if (anamation_pos == 1)
    {
      variation_one(fps,LED);
    }
    else if (anamation_pos == 2)
    {
      variation_two(fps,LED);
    }
    else if (anamation_pos == 3)
    {
      variation_three(fps,LED);
    }
    
    else if (start_sd())
    {
      variation_SD(fps,LED);
    }
    else
    {
      anamation_pos = 0;
    }
  
    print_frame(LED); // prints the LED array to the leds
  }
}

bool variation_zero(byte LED[8][8][8]) //resets the array
{
  run_once = 1;
  var_2_par = 0;
  FPS_LOCATION[0] = 0;
  FPS_LOCATION[1] = 0;
  FPS_LOCATION[2] = 0;
  for (int z = 0; z < 8; ++z)
    {
      for (int y = 0; y < 8; ++y)
      {
        for (int x = 0; x < 8; ++x)
        {
          LED[z][y][x] = 0;
        }
      }
    }
}

bool variation_one(int fps,byte LED[8][8][8]) // This makes pulses of lights in different orientations
{
  if(fps_watch.ms() >= fps)
  {
    fps_watch.restart();
    // Variation begins 
    byte variation = FPS_LOCATION[0] >> 8; // Shift the next 8 bits for location 
    FPS_LOCATION[0] &= 0b0000000011111111;
    if (FPS_LOCATION[0] == 7 and FPS_LOCATION[1] == 7 and FPS_LOCATION[2] == 7)
    {
      variation_zero(LED);
      ++variation;
      if (variation == 4)
      {
        variation = 0;
      }
    }
    
    if (variation == 0)
    {
      //Delete the trail
      for (byte z = 0; z < 8; ++z)
      {
          for (byte y = 0; y < 8; ++y)
        {
            for (byte x = 0; x < 8; ++x)
          {
            if (LED[z][y][x] > 0) // Decrement the LED
            {
              LED[z][y][x] -= 1;
            }
          }
        }
      }
      //Make the trail
      for (int z = FPS_LOCATION[2]; z < 8; ++z)
        {
          for (int y = FPS_LOCATION[1]; y < 8; ++y)
          {
           for (int x = FPS_LOCATION[0]; x < 8; )
            {
              /*
              int brightness = 8;
              for (int trail = x; trail >= 0; --trail)
              {
                LED[z][y][trail] = brightness;
                --brightness;
              }
              */
              LED[z][y][x] = 8;
              ++x;
              FPS_LOCATION[0] = x | (variation << 8);
              FPS_LOCATION[1] = y;
              FPS_LOCATION[2] = z;
              
              return 0;
            }
           FPS_LOCATION[0] = 0 | (variation << 8);
          }
         FPS_LOCATION[1] = 0;
        }
    }
  
    else if (variation == 1)
    {
      //Delete the trail
      for (byte z = 0; z < 8; ++z)
      {
          for (byte y = 0; y < 8; ++y)
        {
            for (byte x = 0; x < 8; ++x)
          {
            if (LED[z][y][x] > 0) // Decrement the LED
            {
              LED[z][y][x] -= 1;
            }
          }
        }
      }
      for (int z = FPS_LOCATION[2]; z < 8; ++z)
        {
          for (int y = FPS_LOCATION[1]; y < 8; ++y)
          {
           for (int x = FPS_LOCATION[0]; x < 8; )
            {
              /*
              int brightness = 8;
              for (int trail = x; trail >= 0; --trail)
              {
                LED[z][trail][y] = brightness;
                --brightness;
              }
              */
              LED[z][x][y] = 8;
              ++x;
              FPS_LOCATION[0] = x | (variation << 8);
              FPS_LOCATION[1] = y;
              FPS_LOCATION[2] = z;
             return 0;
            }
           FPS_LOCATION[0] = 0;
          }
         FPS_LOCATION[1] = 0;
        }
    }
  
    else if (variation == 2)
    {
      //Delete the trail
      for (byte z = 0; z < 8; ++z)
      {
          for (byte y = 0; y < 8; ++y)
        {
            for (byte x = 0; x < 8; ++x)
          {
            if (LED[z][y][x] > 0) // Decrement the LED
            {
              LED[z][y][x] -= 1;
            }
          }
        }
      }
      for (int z = FPS_LOCATION[2]; z < 8; ++z)
        {
          for (int y = FPS_LOCATION[1]; y < 8; ++y)
          {
           for (int x = FPS_LOCATION[0]; x < 8; )
            {
              /*
              int brightness = 8;
              for (int trail = x; trail >= 0; --trail)
              {
                LED[trail][z][y] = brightness;
                --brightness;
              }
              */
              LED[x][z][y] = 8;
              ++x;
              FPS_LOCATION[0] = x | (variation << 8);
              FPS_LOCATION[1] = y;
              FPS_LOCATION[2] = z;
             return 0;
            }
           FPS_LOCATION[0] = 0;
          }
         FPS_LOCATION[1] = 0;
        }
    }
  
    else if (variation == 3)
    {
      //Delete the trail
      for (byte z = 0; z < 8; ++z)
      {
          for (byte y = 0; y < 8; ++y)
        {
            for (byte x = 0; x < 8; ++x)
          {
            if (LED[z][y][x] > 0) // Decrement the LED
            {
              LED[z][y][x] -= 1;
            }
          }
        }
      }
      for (int z = FPS_LOCATION[2]; z < 8; ++z)
        {
          for (int y = FPS_LOCATION[1]; y < 8; ++y)
          {
           for (int x = FPS_LOCATION[0]; x < 8; )
            {
              /*
              int brightness = 8;
              for (int trail = x; trail >= 0; --trail)
              {
                LED[y][trail][z] = brightness;
                --brightness;
              }
              */
              LED[y][x][z] = 8;
              ++x;
              FPS_LOCATION[0] = x | (variation << 8);
              FPS_LOCATION[1] = y;
              FPS_LOCATION[2] = z;
             return 0;
            }
           FPS_LOCATION[0] = 0;
          }
         FPS_LOCATION[1] = 0;
        }
    }
  }
}

bool variation_two(int fps,byte LED[8][8][8]) // This makes random leds turn on and off while having all of them pulse with different brightness
{
  var_2_par = 1;
  if(fps_watch.ms() >= fps)
  {
    fps_watch.restart();
    if(FPS_LOCATION[2] >= 512)// Check if LEDS are all on, if so, make the LEDS turn off
    {
      FPS_LOCATION[1] = FPS_LOCATION[1] & B11111101; // This will make the LEDS turn off
    }
    else if (FPS_LOCATION[2] <= 0)
    {
      FPS_LOCATION[1] = FPS_LOCATION[1] | B00000011;// This will make the LEDS turn on
    }
    
    if (FPS_LOCATION[0] == 32)
    {
      FPS_LOCATION[1] = FPS_LOCATION[1] & B11111110; // This means that the brightness will be decreasing
    }
    else if (FPS_LOCATION[0] == 4)
    {
      FPS_LOCATION[1] = FPS_LOCATION[1] | B00000001; // This means that the brightness will be increasing
    }
    if ((FPS_LOCATION[1] & B00000001) == B00000001)
    {
      ++FPS_LOCATION[0];
    }
    else if ((FPS_LOCATION[1] & B00000001) == B00000000)
    {
      --FPS_LOCATION[0];
    }
    
    for (int z = 0; z < 8; ++z)
      {
        for (int y = 0; y < 8; ++y)
        {
          for (int x = 0; x < 8; ++x)
          {
            //To grab the on data for the random cycle
            bool LED_status = (LED[z][y][x] & B10000000);
            LED[z][y][x] = FPS_LOCATION[0] / 4;// FPS_LOCATION[0] acts as the brightness factor of the LEDs
            //Addts back the LED status
            if (LED_status)
            {
              LED[z][y][x] = LED[z][y][x] | B10000000;
            }
          }
         }
       }
    
    while (1) //Randomly turns an LED on every cycle 
    {
      //Serial.println(FPS_LOCATION[1],BIN);
      //Serial.println(((FPS_LOCATION[1] & B00000010) == B00000010),BIN);
      // selects a random number from 0-7
      int x_loc = random(8); 
      int y_loc = random(8);
      int z_loc = random(8);
      //Serial.println(LED[z_loc][y_loc][x_loc]);
      if (((FPS_LOCATION[1] & B00000010) == B00000010) and ((LED[z_loc][y_loc][x_loc] & B10000000) == 0))
      {
        ++FPS_LOCATION[2]; // To count how many LED's turn on
        LED[z_loc][y_loc][x_loc] = LED[z_loc][y_loc][x_loc] | B10000000;
        break;
      }
      else if (((FPS_LOCATION[1] & B00000010) == B00000000) and ((LED[z_loc][y_loc][x_loc] & B10000000) >= 1))
      {
        --FPS_LOCATION[2]; // To count how many LED's turn off
        LED[z_loc][y_loc][x_loc] = LED[z_loc][y_loc][x_loc] & B01111111;
        break;
      }
     }
    
  }
}

bool variation_three(int fps, byte LED[8][8][8])
{
  if(fps_watch.ms() >= fps)
  {
    fps_watch.restart();
    // This makes a wave in the center that moves up and down while having particles moving past it.
  // First part will make the particles zoom past the wave
  //Move particles
  for (int z = 0; z < 8; ++z)
  {
    for (int y = 0; y < 8; ++y)
    {
      for (int x = 7; x >= 0; --x) // must be backwards checking so it doesn't check a moved particle
      {
        if (LED[z][y][x] == 4)//Check if location is particle: if so, move one pixel
        {
          LED[z][y][x] = 0;
          //spawning
          if (x != 7) // To prevent spawning past LED grid
          {
            LED[z][y][x + 1] = 4;
            LED[z][y][x] = 1; // trail
            if (x != 0) // To prevent spawning past LED grid
            {
              //Delete past trail
              LED[z][y][x - 1] = 0; 
            }
          }
          else // to clear the trail at the last location of the particle
          {
            //Delete past trail
              LED[z][y][x - 1] = 0; 
          }
        }
      }
    }
  }
  //Make knew particles
  byte spawn_chance = random(4); // 0-3
  byte spawn_amount = 0;
  if (spawn_chance == 3) // 1/4 chance of spawning some particles
  {
      spawn_amount = random(20); // 0-19
      if (spawn_amount <= 9)// Spawn one
      {
        spawn_amount = 1;
      }
      else if (spawn_amount > 9 and spawn_amount != 19)// Spawn 3
      {
        spawn_amount = 3;
      }
      else if (spawn_amount == 19)// Spawn 8
      {
        spawn_amount = 7;
      }
    }
    while (spawn_amount)// spawn the particles
    {
      --spawn_amount; // decrement every spawn
      byte z = random(8);//0-7
      byte y = random(8);
      LED[z][y][0] = 4; //brightness 4
    }
    //Wave motion: This will consists of 4 LEDs trailing up and down with a tail
    // Erase what was there
    float radian_1 = FPS_LOCATION[0] / 10.0; // Make into float for decimal
    //Create waves starting with the first 2 block cube
    byte z_change = (3.5 * cos(radian_1)) + 3;
    
    LED[z_change + 1][3    ][3] = 0;
    LED[z_change + 1][3 + 1][3] = 0;
    LED[z_change    ][3 + 1][3] = 0;
    LED[z_change    ][3    ][3] = 0;
    
    // tail 1
    byte z_change1 = (3.5 * cos(radian_1 + 0.84)) + 3; // discplaced by one LED, this is happening for all values
    
    LED[z_change1 + 1][3    ][4] = 0;
    LED[z_change1 + 1][3 + 1][4] = 0;
    LED[z_change1    ][3 + 1][4] = 0;
    LED[z_change1    ][3    ][4] = 0;
    // tail 2
    byte z_change2 = (3.5 * cos(radian_1 + 1.231)) + 3;
    
    LED[z_change2 + 1][3    ][5] = 0;
    LED[z_change2 + 1][3 + 1][5] = 0;
    LED[z_change2    ][3 + 1][5] = 0;
    LED[z_change2    ][3    ][5] = 0;
    // tail 3
    byte z_change3 = (3.5 * cos(radian_1 + 1.57)) + 3;
    LED[z_change3 + 1][3    ][6] = 0;
    LED[z_change3 + 1][3 + 1][6] = 0;
    LED[z_change3    ][3 + 1][6] = 0;
    LED[z_change3    ][3    ][6] = 0;
    // tail 4
    byte z_change4 = (3.5 * cos(radian_1 + 1.911)) + 3;
    LED[z_change4 + 1][3    ][7] = 0;
    LED[z_change4 + 1][3 + 1][7] = 0;
    LED[z_change4    ][3 + 1][7] = 0;
    LED[z_change4    ][3    ][7] = 0;
    // Erasing DONE ---------------------------------------
    
    // FPS_LOCATION[0]: x for cos(x), increments .2 for now 
    FPS_LOCATION[0] += 3;
    radian_1 = FPS_LOCATION[0] / 10.0; // Make into float for decimal
    //Create waves starting with the first 2 block cube
    z_change = (3.5 * cos(radian_1)) + 3;
    
    LED[z_change + 1][3    ][3] = 8;
    LED[z_change + 1][3 + 1][3] = 8;
    LED[z_change    ][3 + 1][3] = 8;
    LED[z_change    ][3    ][3] = 8;
    
    // tail 1
    z_change1 = (3.5 * cos(radian_1 + 0.84)) + 3; // discplaced by one LED, this is happening for all values
    LED[z_change1 + 1][3    ][4] = 8;
    LED[z_change1 + 1][3 + 1][4] = 8;
    LED[z_change1    ][3 + 1][4] = 8;
    LED[z_change1    ][3    ][4] = 8;
    // tail 2
    z_change2 = (3.5 * cos(radian_1 + 1.231)) + 3;
    LED[z_change2 + 1][3    ][5] = 8;
    LED[z_change2 + 1][3 + 1][5] = 8;
    LED[z_change2    ][3 + 1][5] = 8;
    LED[z_change2    ][3    ][5] = 8;
    // tail 3
    z_change3 = (3.5 * cos(radian_1 + 1.57)) + 3;
    LED[z_change3 + 1][3    ][6] = 8;
    LED[z_change3 + 1][3 + 1][6] = 8;
    LED[z_change3    ][3 + 1][6] = 8;
    LED[z_change3    ][3    ][6] = 8;
    // tail 4
    z_change4 = (3.5 * cos(radian_1 + 1.911)) + 3;
    LED[z_change4 + 1][3    ][7] = 8;
    LED[z_change4 + 1][3 + 1][7] = 8;
    LED[z_change4    ][3 + 1][7] = 8;
    LED[z_change4    ][3    ][7] = 8;
  }
}

bool variation_SD(int fps, byte LED[8][8][8])
{
  for (byte i = 0; i < cube_files_amount; ++i)
  {
    if ((amount_variations + i) == anamation_pos) // Choose an SD card variation
    {
      if(fps_watch.ms() >= fps)
      {
        if (run_once) // Complete all of the run once for the file, this will increase the speed of writing each frame
        {
          run_once = 0;
          dataFile.close();
          char file[cube_files_size[i] + 1];
          for (byte v = 0; v < cube_files_size[i] + 1; ++v)
          {
            if (v == cube_files_size[i])
            {
              file[v] = 0;
            }
            file[v] = cube_files[i][v];
          }
          dataFile = SD.open(file);
        }
        fps_watch.restart();
        // Get to the right location of the file everytime
        //Writing data
        for(byte z = 7; z < 8; --z)
        {
          for(byte y = 0; y < 8; ++y)
          {
            dataFile.read(LED[z][y],8);
          }
        }
        if (dataFile.peek() == -1) // End of file --- reset
          {
            dataFile.seek(0);
            return 1;
          }
      }
    }
    if ((amount_variations + cube_files_amount - 1) < anamation_pos)// Variation is done with SD card
    {
      anamation_pos = 0;
    }
  }
  return 0;
}

bool start_sd()
{
  if (!sd_ready)
  {
      sd_ready = SD.begin(chipSelect);
      delay(100);
      if (sd_ready)
      {
        File root = SD.open("/");
        //Serial.print("Root name: ");
        //Serial.println(root.name());
        byte test_ammount = 200;
        while (1)
        {
          --test_ammount;
          File entry =  root.openNextFile();

          if (!entry or !test_ammount) 
          {
            // no more files
            break;
          }
          if (!entry.isDirectory())
          {
            byte file_size = 0;
            byte run_pos = 0;
            bool correct_file = 0;
            while (true)
            {
              if(entry.name()[run_pos] == '.' and entry.name()[run_pos+1] == 'C' and entry.name()[run_pos+2] == 'U' and entry.name()[run_pos+3] == 'B')
              {
                file_size += 4; // this is for the .CUB
                correct_file = 1;
                break;
              }
              else if(run_pos > 12) // Incorrect file
              {
                break;
              }
              ++run_pos;
              ++file_size;
            }
            if (correct_file and files_amount > cube_files_amount) // Copy file name into list
            {
              cube_files_size[cube_files_amount] = file_size;
              for (byte i = 0; i < file_size; ++i)
              {
                cube_files[cube_files_amount][i] = entry.name()[i];
              }
              ++cube_files_amount;
            }
          }
          entry.close();
        }
        root.close();
      }
  }
  return sd_ready;
}

void print_frame(byte LED[8][8][8])
{
  int pos = 0;
  for (byte z = 0; z < 8; ++z)
  {
    for (byte y = 0; y < 8; ++y)
    {
      for (byte x = 0; x < 8; ++x)
      {
        bool value = (pwm_pos < (LED[z][y][x] & B00001111)); // Only select first three bits 0-7
        if (var_2_par)
        {
          value = (pwm_pos < (LED[z][y][x] & B00001111)) and (LED[z][y][x] & B10000000);
        }
        print_led(pos, value);
        ++pos;
      }
    }
  }
  if(pwm_pos == pwm_res)//resets
  {
    pwm_pos = 0;
  }
  else // increment
  {
    ++pwm_pos;
  }
}

void print_led(int location, bool value) // Max location number 511
{
  /*
  byte l1 = (location >= 0 and location < 64 and value) << 4;//1
  byte l2 = (location >= 64 and location < 128 and value) << 3; //2
  byte l3 = (location >= 128 and location < 192 and value) << 5; //3
  */
  //digitalWrite(data_out, value);

  byte C_change = PORTC & B11000111;
  
  bool bit_9 = location & 0b100000000;
  byte B_change = PORTB & B11111100;
  PORTB = (B_change | bit_9 | value << 1);
  PORTD = (location & B11111111);
  PORTC = (C_change | (location >= 0 and location < 64 and value) << 4 | (location >= 64 and location < 128 and value) << 3 | (location >= 128 and location < 192 and value) << 5);
  /*
  if ((location & 0b00000111) == 1)
  {
     for (int i = 0; i < 0; ++i)// 550
     {
      __asm__("nop\n\t"); 
     }
  }
  */
}

/*
void print_led(int location, bool value) // Max location value 511
{
  digitalWrite(data_out, value);
  bool bit_9 = location & 0b100000000;
  byte B_change = PORTB & B11111110;
  PORTB = (B_change | bit_9);
  PORTD = (location & B11111111);
}
*/
