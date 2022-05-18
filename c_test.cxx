//code that listens to the uart port for gps coords, and otherwise dumps the data to a file
#include <iostream>
#include <fstream>
#include <ostream>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <termios.h>
#include <cstring>
#include <sstream>

using namespace std;

class config
{    
    public:
    string file_dir;
    string file_name;
    double goal_lat;
    double goal_lon;
    double goal_pulse_rate;
    double goal_amplitude;

    void load_config();
    void set_config();
};
void config::load_config()
{
    fstream file("/config/read_in_config.dat");
    string line="";
    while(getline(file,line))
    {
        istringstream sin(line.substr(line.find("=")+1));
        if((int)line.find("file_dir")!=-1) sin>>file_dir;
        else if ((int)line.find("file_name")!=-1) sin>>file_name;
        else if ((int)line.find("goal_lat")!=-1) sin >>goal_lat;
        else if ((int)line.find("goal_lon")!=-1) sin >>goal_lon;
        else if ((int)line.find("goal_pulse_rate")!=-1) sin >>goal_pulse_rate;
        else if ((int)line.find("goal_amplitude")!=-1) sin >>goal_amplitude;
    }
    file.flush();
    file.close();
};
void config::set_config()
{
    fstream file("/config/read_in_config.dat");
    file<<"file_dir="<<file_dir<<endl;
    file<<"file_name="<<file_name<<endl;
    file<<"goal_lat="<<goal_lat<<endl;
    file<<"goal_lon="<<goal_lon<<endl;
    file<<"goal_pul_rate="<<goal_pulse_rate<<endl;
    file<<"goal_amplitude="<<goal_amplitude<<endl;
    file.flush();
    file.close();
};

class gps_dump
{
    public:
        char * buffer;

        short int max_buff_size=2048;

        void dumping(string filename,char * buffer,short index,short n_to_dump);
        

};
void gps_dump::dumping(string filename,char * buffer,short index,short n_to_dump)
{
    fstream outfile(filename.c_str());
    short temp_spot=index;
    for(int i = index;i<index+n_to_dump;i++)
    {
        if(index+i>max_buff_size)temp_spot=index+i-max_buff_size;
        outfile>>buffer[temp_spot];
    }
    outfile.flush();
    outfile.close();

};
void decode_coords(char * returned_lat, char * returned_lon, double * lat, double * lon);
bool should_pulse(double lat, double lon);


const string uart_port="/dev/ttyS1";
const int uart_speed=115200;
const string config_file="";

int main() 
{

    const char sync_bit=0xb5;
    const char preamble=0x62;
    const char ubx_class=0x01;
    const char pvt_id=0x07;
    
    
    char packet_size;
    char buf[2048];
    gps_dump GPS;
    GPS.buffer=buf;
    double lon,lat;
    
    config=open(config_file.c_str(),"r");
    string temp_fil="";
    
    string output_file="/data/";
    output_file+=temp_fil;
    output_file+=".dat";

    struct tty;
    uart=open(uart_port);
    int index;
    int first_byte,last_byte;
    bool to_push_back;
    while(false)//for now leave false but should be true
    {
        //try initial
    int num_bytes_in_buf=read(uart,&buf+index,5)

    for(int i = index;i<num_bytes_in_buf;i++)
    {
        if(buf[i]==sync_bit && buf[i+1]==preamble)
        {
            packet_size=atof(buf[index+4]);
            first_byte=i;
            last_byte=packet_size+i+2;
            if(last_byte>num_bytes_in_buf+first) //grab more
            if(last_byte>2048)//loop around
            break;
        }

    char returned_lon[4];
    char returned_lat[4];
    //place recieved bytes into returned arrays
    
    decode_coords(&returned_lat, &returned_lon,&lat,&lon);
    should_pulse(lon,lat);
    
    }
    


}

void decode_coords(char * returned_lat, char * returned_lon, double * lat, double * lon)
{
    //convert returned values to human readable form
}
bool should_pulse(double lat,double lon) //handles reading/writing pusling file which "will" be changed so a daemon reads that file to decide pusling
{
    //more complicated stuff
    bool pulse=true;
    fstream file("/config/pulse.txt")
    string temp="";
    getline(temp,file);
    bool file_pulse=(atof(temp)==1);

    if(pulse==file_pulse)
    {
        //no change
    }

    else
    {
        write(file,pulse);
    }

    file.flush();
    file.close();

    return pulse;
}
