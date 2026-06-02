import { useEffect, useState } from 'react';
import * as signalR from '@microsoft/signalr';

export const useSignalR = () => {
  const [connection, setConnection] = useState<signalR.HubConnection | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    
    // Only connect if we have a token
    if (!token) return;

    const hubUrl = import.meta.env.VITE_API_URL 
      ? import.meta.env.VITE_API_URL.replace('/api/hermes', '/hub/notifications') 
      : 'http://localhost:5000/hub/notifications';

    const newConnection = new signalR.HubConnectionBuilder()
      .withUrl(hubUrl, {
        accessTokenFactory: () => token,
      })
      .withAutomaticReconnect()
      .build();

    setConnection(newConnection);
  }, []);

  useEffect(() => {
    if (connection) {
      connection.start()
        .then(() => {
          console.log('SignalR Connected.');
        })
        .catch(e => console.log('SignalR Connection Error: ', e));
    }

    return () => {
      if (connection) {
        connection.stop();
      }
    };
  }, [connection]);

  return connection;
};
