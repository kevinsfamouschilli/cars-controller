/*
    C ECHO client example using sockets

Taken from:
http://www.binarytides.com/server-client-example-c-sockets-linux/

*/
#include<unistd.h> //sleep
#include<stdio.h> //printf
#include<string.h>    //strlen
#include<sys/socket.h>    //socket
#include<arpa/inet.h> //inet_addr
 
int main(int argc , char *argv[])
{
    int sock;
    struct sockaddr_in server;
    char message[1000] = "{\"00:06:66:61:A9:59\":[1,43,874,300,0,0,0,0],\"00:06:66:61:A3:48\":[1,299,605,250,0,0,0,0]}";
    char messagetwo[1000] = "{\"00:06:66:61:A9:59\":[1,43,0,0,0,0,0,0],\"00:06:66:61:A3:48\":[1,299,0,0,0,0,0,0]}";
     
    //Create socket
    sock = socket(AF_INET , SOCK_STREAM , 0);
    if (sock == -1)
    {
        printf("Could not create socket");
    }
    puts("Socket created");
     
    server.sin_addr.s_addr = inet_addr("127.0.0.1");
    server.sin_family = AF_INET;
    server.sin_port = htons( 1520 );
 
    //Connect to remote server
    if (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0)
    {
        perror("connect failed. Error");
        return 1;
    }
     
    puts("Connected\n");
  
	// TODO: Use actual computer vision data rather than dummy data!

	//Send first computer vision data
	if( send(sock , message , strlen(message) , 0) < 0)
	{
	    puts("Send failed");
	    return 1;
        }
	
	// Sleep so car drives for 1 second
	sleep(1);

	//Send second computer vision data data to stop car
	if( send(sock , messagetwo , strlen(messagetwo) , 0) < 0)
	{
	    puts("Send failed");
	    return 1;
        }
     
    return 0;
}