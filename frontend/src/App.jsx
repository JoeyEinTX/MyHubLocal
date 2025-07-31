import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./hooks/useTheme";
import Home from "./pages/Home";
import Settings from "./pages/Settings";

function AppContent() {
  return (
    <Router>
      <div className="min-h-screen bg-background text-text">
        {/* Main Content - No padding since PageHeader handles its own layout */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/scenes" element={
            <div className="min-h-screen bg-background">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="text-center py-12 text-text">
                  <h1 className="text-3xl font-bold mb-4">Scenes</h1>
                  <p className="text-text-secondary">Smart home automation scenes coming soon!</p>
                </div>
              </div>
            </div>
          } />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>
    </Router>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
