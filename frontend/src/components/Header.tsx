import React from "react";

const Header: React.FC = () => {
  const handleLogoError = (
    e: React.SyntheticEvent<HTMLImageElement, Event>
  ) => {
    const fallbackSvg =
      "data:image/svg+xml;utf8," +
      encodeURIComponent(`
        <svg xmlns='http://www.w3.org/2000/svg' width='180' height='40'>
          <rect width='100%' height='100%' fill='#0c77ab'/>
          <text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='white' font-family='Arial' font-size='14'>VPBank Logo</text>
        </svg>
      `);
    (e.currentTarget as HTMLImageElement).src = fallbackSvg;
  };

  return (
    <header className="w-full bg-gradient-to-r from-[#0c77ab] to-[#0ea96d] shadow-lg">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center h-16">
          {/* Logo and Solution Name */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <img
                src="/LogoVPBank_Header.svg"
                alt="VPBank Logo"
                className="h-8 w-auto"
                onError={handleLogoError}
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

export function HeaderPreview() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      {/* Standalone preview area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-gray-500">
          This is a standalone header preview. Add your page content here.
        </div>
      </main>
    </div>
  );
}
