// Here 2-6 pins uses for first five of ports which gives signal
// to board and 8-12 pins for second five which block signal on board

#define INPUT_TYPE_STOP            1
#define INPUT_TYPE_SINGLE_SYMBOL   2
#define INPUT_TYPE_TEXT_START      3
#define INPUT_TYPE_NEXT_SYMBOL     4
#define OUTPUT_CONFIRMATION   10

#define STATE_STOP            1
#define STATE_SINGLE_SYMBOL   2
#define STATE_TRANSLATION     3

void setup() {
  Serial.begin(9600);
  for (int i = 2; i <= 6; ++i)
    pinMode(i, OUTPUT);
  for (int i = 8; i <= 12; ++i)
    pinMode(i, OUTPUT);
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
}

byte readByte();
int readInt();
long readLong();

void loop() {
  byte state = STATE_STOP;
  bool* lines;
  byte* signal_map;
  int pause;
  int repeat;
  bool letter_done;
  byte flag;
  bool s = false;
  while (true) {
    if (Serial.available()) {
      delay(10);
      flag = readByte();
      if (flag == INPUT_TYPE_STOP) {
        stop_letter();
        state = STATE_STOP;
      }
      else if (flag == INPUT_TYPE_SINGLE_SYMBOL) {
        stop_letter();
        pause = readInt();
        long letter_code = readLong();
        byte line_code = readByte();
        lines = parseLine(line_code);
        signal_map = parseLetter(letter_code);
        state = STATE_SINGLE_SYMBOL;
      }
      else if (flag == INPUT_TYPE_TEXT_START) {
        stop_letter();
        state = STATE_TRANSLATION;
        pause = readInt();
        repeat = readInt();
        byte line_code = readByte();
        lines = parseLine(line_code);
        letter_done = true;
      } 
      else if (flag == INPUT_TYPE_NEXT_SYMBOL) {
        if (state == STATE_TRANSLATION) {
          long letter_code = readLong();
          signal_map = parseLetter(letter_code);
          Serial.write(OUTPUT_CONFIRMATION);
          letter_done = false;
        }
      }
    }

    if (state == STATE_SINGLE_SYMBOL) {
      for (int i = 0; i < 5; ++i) {
        if(!lines[i]) continue;
        PORTD = (PORTD & B10000011) | 1 << (i+2);
        PORTB = (PORTB & B11100000) | signal_map[i];
        delay(pause);
      }
      stop_letter();
    }
    else if (state == STATE_TRANSLATION) {
      if (!letter_done) {
        for (int j = 0; j < repeat; ++j) {
          for (int i = 0; i < 5; ++i) {
            if(!lines[j]) continue;
            PORTD = (PORTD & B10000011) | 1 << (i+2);
            PORTB = (PORTB & B11100000) | signal_map[i];
            delay(pause);
          }
        }
        stop_letter();
        letter_done = true;
      }
    }
  }
}

void stop_letter() {
  PORTD &= B10000011;
  PORTB &= B11100000;
}

bool* parseLine(byte line_code) {
  static bool lines[5];
  for (int i = 0; i < 5; ++i) {
    lines[i] = line_code >> i & 1;
  }
  return lines;
}

byte* parseLetter(long letter_code) {
  static byte signalMap[5];
  for (int i = 0; i < 5; ++i) {
    signalMap[i] = 0;
    for (int j = 0; j < 5; ++j) {
      signalMap[i] |= !(letter_code >> (j*5 + i) & 1) << j;
    }
  }
  return signalMap;
}

byte readByte() {
  return Serial.read();
}

int readInt() {
  int part1=Serial.read(), part2=Serial.read();
  int result = part1<<8 | part2;
  return result;
}

long readLong() {
  long part1=Serial.read(), part2=Serial.read(),
       part3=Serial.read(), part4=Serial.read();
  long result = part1<<24 | part2<<16 | part3<<8 | part4;
  return result;
}
