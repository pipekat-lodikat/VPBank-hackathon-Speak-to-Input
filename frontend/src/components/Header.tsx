import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="w-full bg-gradient-to-r from-[#0c77ab] to-[#0ea96d] shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center h-16">
          {/* Logo and Solution Name */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <img 
                src="/logo-vpbank-2-1400x327.webp" 
                alt="VPBank Logo" 
                className="h-8 w-auto"
              />
            </div>
            <div>
              <h1 className="text-white text-lg font-semibold">
                VPBank Hackathon Voice Agent
              </h1>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;