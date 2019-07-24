#include "LeptonThread.h"
#include <cstdlib>
#include <fstream>
#include <iostream>


#include "Palettes.h"
#include "SPI.h"
#include "Lepton_I2C.h"

#define PACKET_SIZE 164
#define PACKET_SIZE_UINT16 (PACKET_SIZE/2) //PACKET_SIZE_UINT16: 82
#define PACKETS_PER_FRAME 60
#define FRAME_SIZE_UINT16 (PACKET_SIZE_UINT16 * PACKETS_PER_FRAME) //FRAME_SIZE_UINT16: 82*60=4920
#define FPS 27;

using namespace std;

LeptonThread::LeptonThread() : QThread(){
}

LeptonThread::~LeptonThread() {
}

void LeptonThread::run()
{
	int dataCount = 0;
	float maxTemp = 0.0;
	
	std::ofstream fp;
	fp.open("tmpData.txt", ios::out); //std::ios_base::app
	
	//create the initial image
	myImage = QImage(80, 60, QImage::Format_RGB888); //80*60

	//open spi port
	SpiOpenPort(0);
	
	//cout << FRAME_SIZE_UINT16 << endl;
	
	while(true) {

		//read data packets from lepton over SPI
		int resets = 0;
		
		//cout << sizeof(uint8_t) * PACKET_SIZE << endl;
		int flg = 1;
		for (register int j = 0; j < PACKETS_PER_FRAME ; j++) { 
			//if it's a drop packet, reset j to 0, set to -1 so he'll be at 0 again loop
			
			if(flg==1){ flg=0;}
							
			read(spi_cs0_fd, result + sizeof(uint8_t) * PACKET_SIZE * j, sizeof(uint8_t) * PACKET_SIZE);
			
			int packetNumber = result[j * PACKET_SIZE + 1]; // result size(9840) = PACKET_SIZE * PACKETS_PER_FRAME = 60*164
			//printf("packetNumber:%d, j=%d, resets=%d, result index=%d\n" ,packetNumber, j, resets, (j * PACKET_SIZE + 1));
			
			// drop packet issue
			if (packetNumber != j) {
				j = -1;
				resets += 1;
				usleep(1000);
				//Note: we've selected 750 resets as an arbitrary limit, since there should never be 750 "null" packets between two valid transmissions at the current poll rate
				//By polling faster, developers may easily exceed this count, and the down period between frames may then be flagged as a loss of sync
				if (resets == 750) {
					SpiClosePort(0); // close port
					usleep(750000);  // us(1s=1,000,000 us)
					SpiOpenPort(0);  // open port
				}
			}
		}
		
		//if (resets >= 30) {
			//qDebug() << "done reading, resets: " << resets;
		//}

		frameBuffer = (uint16_t *)result;
		int row, column;
		uint16_t value;
		uint16_t minValue = 65535;
		uint16_t maxValue = 0;
		
		for (register int i = 0; i < FRAME_SIZE_UINT16; i++) { //FRAME_SIZE_UINT16=4920
			//skip the first 2 uint16_t's of every packet, they're 4 header bytes
			if (i % PACKET_SIZE_UINT16 < 2) {
				continue;
			}
			
			//flip the MSB and LSB at the last second
			int temp = result[i * 2];
			result[i * 2] = result[i * 2 + 1];
			result[i * 2 + 1] = temp;
			
			value = frameBuffer[i];
			if (value > maxValue) {
				maxValue = value;
				//cout << "change maxValue: " << maxValue << endl;
			}			
			if (value < minValue) {
				minValue = value;
				//cout << "change minValue: " << minValue << endl;
			}
			
			column = i % PACKET_SIZE_UINT16 - 2;
			row = i / PACKET_SIZE_UINT16 ;
		}
		
		//cout << "minValue: " << minValue << endl;
		//cout << "maxValue: " << maxValue << endl;
		//cout << endl;
		maxTemp = (((float) maxValue * 90/16384) - 10);
		printf("maxTemp:%.2f\n", maxTemp);
		//printf("maxval:%d\n", maxValue);
		
		// record result		
		dataCount += 1;		
		if (dataCount >= 5){
			SpiClosePort(0);
			
			//std::ofstream fp;
			//fp.open("test.txt", std::ios_base::app);
			fp << maxTemp; 	 
			fp.close();
			
			std::exit(EXIT_SUCCESS);
		}else{ fp << maxTemp << ",";}		
		
		float diff = maxValue - minValue;
		float scale = 255/diff; // (0-65535) per scale transfer to gray val(0-255)
		QRgb color;
		
		for (register int i = 0; i < FRAME_SIZE_UINT16; i++) {	
			if(i % PACKET_SIZE_UINT16 < 2) {
				continue;
			}
			value = (frameBuffer[i] - minValue) * scale; //value(gray val 0-255)
			
			const int *colormap = colormap_rainbow; // colormap_ironblack
			color = qRgb(colormap[3 * value], colormap[3 * value + 1], colormap[3 * value + 2]);
			column = (i % PACKET_SIZE_UINT16 ) - 2;
			row = i / PACKET_SIZE_UINT16;
			myImage.setPixel(column, row, color); //point(x,y) change color 
		}

		//lets emit the signal for update
		emit updateImage(myImage);
	}
	
	//finally, close SPI port just bcuz
	SpiClosePort(0);
}

void LeptonThread::performFFC() {
	//perform FFC
	lepton_perform_ffc();
}

