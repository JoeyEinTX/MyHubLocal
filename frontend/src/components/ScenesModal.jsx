import React, { useState, useEffect } from 'react';
import { scenesAPI } from '../api.js';

const ScenesModal = ({ isOpen, onClose }) => {
  const [scenes, setScenes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activatingScene, setActivatingScene] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchScenes();
    }
  }, [isOpen]);

  const fetchScenes = async () => {
    try {
      setLoading(true);
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-background border border-border rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-2xl font-bold text-primary tracking-tight">Scenes</h2>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-xl bg-secondary/50 hover:bg-secondary transition-colors duration-200 flex items-center justify-center text-text-secondary hover:text-primary"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {message && (
            <div className={`mb-6 p-4 rounded-xl ${
              message.startsWith('✅') 
                ? 'bg-success/10 text-success border border-success/20' 
                : 'bg-warning/10 text-warning border border-warning/20'
            }`}>
              {message}
            </div>
          )}

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-secondary/20 rounded-xl p-6 animate-pulse">
                  <div className="w-16 h-16 bg-secondary/30 rounded-2xl mx-auto mb-4"></div>
                  <div className="h-6 bg-secondary/30 rounded-lg mb-2"></div>
                  <div className="h-4 bg-secondary/30 rounded-lg mb-4"></div>
                  <div className="h-10 bg-secondary/30 rounded-xl"></div>
                </div>
              ))}
            </div>
          ) : (
            <>
              <p className="text-text-secondary mb-6 text-center">
                Activate predefined scenes to control multiple devices at once
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {scenes.map((scene) => (
                  <div
                    key={scene.id}
                    className="bg-secondary/20 backdrop-blur-sm border border-border rounded-xl p-6 hover:bg-secondary/30 transition-all duration-200 hover:scale-[1.02] shadow-lg hover:shadow-xl"
                  >
                    <div className="flex flex-col items-center text-center space-y-4">
                      <div className="w-16 h-16 bg-accent/10 rounded-2xl flex items-center justify-center text-3xl">
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
                        className={`w-full px-4 py-3 rounded-xl font-medium transition-all duration-200 ${
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
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScenesModal;
