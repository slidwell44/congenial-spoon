import { createContext } from 'react';

export const CurrentUserContext = createContext({
  uid: '00000000-0000-0000-0000-000000000000',
  role: 'MANAGER',
  name: 'Demo Manager'
});

