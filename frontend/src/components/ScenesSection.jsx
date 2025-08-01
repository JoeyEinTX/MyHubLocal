import React, { useState, useEffect } from 'react';
import { scenesAPI } from '../api.js';

const ScenesSection = () => {
  const [scenes, setScenes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activatingScene, setActivatingScene] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchScenes();
  }, []);

  const fetchScenes = async () => {
    try {
      const response = await scenesAPI.getScenes();
      setScenes(response.data);
    } catch (error) {
      console.error('Failed to fetch scenes:', error);
      setMessage('Failed to load scenes');
    } finally {
      setLoading(false);
    }
  };

  const handleActivateScene = async (sceneId) => {
    setActivatingScene(sceneId);
    setMessage('');
    
    try {
      const response = await scenesAPI.activateScene(sceneId);
      if (response.data.success) {
        setMessage(`✅ ${response.data.message}`);
      } else {
        setMessage(`❌ ${response.data.message}`);
      }
    } catch (error) {
      console.error('Failed to activate scene:', error);
      setMessage(`❌ Failed to activate scene: ${error.response?.data?.detail || error.message}`);
    } finally {
      setActivatingScene(null);
      // Clear message after 5 seconds
      setTimeout(() => setMessage(''), 5000);
    }
  };

  const getSceneIcon = (sceneId) => {
    switch (sceneId) {
      case 'scene_all_on':
        return '💡';
      case 'scene_all_off':
        return '🌙';
      case 'scene_dusk_to_sunrise':
        return '🌅';
      case 'scene_sunset_to_11pm':
        return '🌇';
      default:
        return '🎬';
    }
  };

  if (loading) {
    return (
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-primary mb-6 tracking-tight">Scenes</h2>
        <div className="text-text-secondary">Loading scenes...</div>
      </div>
    );
  }

  return (
    <div className="mb-8">
      <h2 className="text-2xl font-bold text-primary mb-6 tracking-tight">Scenes</h2>
      
      {message && (
        <div className={`mb-4 p-4 rounded-xl ${
          message.startsWith('✅') 
            ? 'bg-success/10 text-success border border-success/20' 
            : 'bg-warning/10 text-warning border border-warning/20'
        }`}>
          {message}
        </div>
      )}
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {scenes.map((scene) => (
          <div
            key={scene.id}
            className="bg-secondary/20 backdrop-blur-sm border border-border rounded-xl p-6 hover:bg-secondary/30 transition-all duration-200 hover:scale-[1.02] shadow-lg hover:shadow-xl"
          >
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="text-4xl mb-2">
                {getSceneIcon(scene.id)}
              </div>
              
              <div className="space-y-2">
                <h3 className="font-semibold text-primary text-lg leading-tight">
                  {scene.name}
                </h3>
                <p className="text-text-secondary text-sm leading-relaxed">
                  {scene.description}
                </p>
              </div>
              
              <button
                onClick={() => handleActivateScene(scene.id)}
                disabled={activatingScene === scene.id}
                className={`w-full px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
                  activatingScene === scene.id
                    ? 'bg-secondary text-text-secondary cursor-not-allowed'
                    : 'bg-accent text-white hover:brightness-110 hover:scale-[1.02] shadow-md hover:shadow-lg'
                }`}
              >
                {activatingScene === scene.id ? (
                  <span className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-text-secondary border-t-transparent rounded-full animate-spin"></div>
                    <span>Activating...</span>
                  </span>
                ) : (
                  'Activate'
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ScenesSection;
