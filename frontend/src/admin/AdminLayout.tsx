import React, { useState } from 'react';
import AdminLogin from './AdminLoginNew';
import AdminPanel from './AdminPanel';
import Admin2FASetup from './Admin2FASetup';

type AuthStep = 'login' | '2fa' | 'authenticated';

interface TwoFactorData {
  tempToken: string;
  provisioningUri: string | null;
}

const AdminLayout: React.FC = () => {
  const [authStep, setAuthStep] = useState<AuthStep>('login');
  const [twoFactorData, setTwoFactorData] = useState<TwoFactorData | null>(null);


  const handleTwoFactorRequired = (data: TwoFactorData) => {
    setTwoFactorData(data);
    setAuthStep('2fa');
  };

  const handleAuthSuccess = () => {
    setAuthStep('authenticated');
    setTwoFactorData(null);
  };

  const handleLogout = () => {
    setAuthStep('login');
  };

  if (authStep === 'authenticated') {
    return <AdminPanel onLogout={handleLogout} />;
  }

  if (authStep === '2fa' && twoFactorData) {
    return (
      <Admin2FASetup
        tempToken={twoFactorData.tempToken}
        provisioningUri={twoFactorData.provisioningUri}
        onAuthSuccess={handleAuthSuccess}
      />
    );
  }

  return (
    <AdminLogin
      onAuthSuccess={handleAuthSuccess}
      onTwoFactorRequired={handleTwoFactorRequired}
    />
  );
};

export default AdminLayout;
