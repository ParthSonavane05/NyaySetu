import React, { useState } from 'react';
import LandingPage from './components/landing/LandingPage';
import AuthPage from './components/auth/AuthPage';
import { FIRM_ROLES } from './constants/roles';
import FirmWorkspace from './components/workspace/FirmWorkspace';

export default function App() {
  const [currentView, setCurrentView] = useState('landing'); // 'landing' | 'auth' | 'workspace'
  const [userRole, setUserRole] = useState('partner'); // 'partner' | 'associate' | 'paralegal' | 'researcher'
  const [activeMatter, setActiveMatter] = useState('809'); // '809' | '412' | '105'

  const [firmUser, setFirmUser] = useState({
    role: FIRM_ROLES[0],
    email: 'advocate@mehtachambers.in',
    firmName: 'Mehta & Associates Law Chambers',
  });

  const handleNavigateToAuth = (roleId = 'partner') => {
    setUserRole(roleId);
    setCurrentView('auth');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleBackToLanding = () => {
    setCurrentView('landing');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLoginSuccess = (userData) => {
    setFirmUser(userData);
    if (userData?.role?.id) {
      setUserRole(userData.role.id);
    }
    setCurrentView('workspace');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSignOut = () => {
    setCurrentView('landing');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRoleChange = (newRole) => {
    setUserRole(newRole.id);
    setFirmUser((prev) => ({
      ...prev,
      role: newRole,
      email: newRole.defaultEmail || prev.email,
    }));
  };

  if (currentView === 'auth') {
    return (
      <AuthPage
        initialRoleId={userRole}
        onBackToLanding={handleBackToLanding}
        onLoginSuccess={handleLoginSuccess}
      />
    );
  }

  if (currentView === 'workspace') {
    return (
      <FirmWorkspace
        currentUser={firmUser}
        currentRole={firmUser.role}
        userRole={userRole}
        activeMatter={activeMatter}
        onMatterChange={setActiveMatter}
        firmUser={firmUser}
        onSignOut={handleSignOut}
        onRoleChange={handleRoleChange}
      />
    );
  }

  return (
    <LandingPage
      onNavigateToAuth={handleNavigateToAuth}
    />
  );
}
