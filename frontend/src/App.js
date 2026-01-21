import React, { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { toast, Toaster } from "sonner";
import { 
  Upload, 
  Scan, 
  AlertTriangle, 
  Package, 
  TrendingUp,
  Clock,
  Shield,
  Activity,
  ChevronRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  // Fetch stats and history on mount
  useEffect(() => {
    fetchStats();
    fetchHistory();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API}/history`);
      setHistory(response.data);
    } catch (error) {
      console.error("Error fetching history:", error);
    }
  };

  const handleImageSelect = (file) => {
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please select a valid image file');
      return;
    }

    setSelectedImage(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleImageSelect(file);
  }, []);

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    handleImageSelect(file);
  };

  const analyzeImage = async () => {
    if (!selectedImage) {
      toast.error('Please select an image first');
      return;
    }

    setAnalyzing(true);
    console.log('Starting analysis for:', selectedImage.name);
    
    try {
      // Convert to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        try {
          const base64 = reader.result.split(',')[1];
          console.log('Image converted to base64, length:', base64.length);
          console.log('Sending to API:', `${API}/analyze`);
          
          const response = await axios.post(`${API}/analyze`, {
            image_base64: base64,
            image_name: selectedImage.name
          });

          console.log('Analysis complete:', response.data);
          setAnalysis(response.data);
          toast.success('Analysis complete!');
          
          // Refresh stats and history
          fetchStats();
          fetchHistory();
        } catch (error) {
          console.error('Error in analysis request:', error);
          toast.error(`Analysis failed: ${error.message}`);
          setAnalyzing(false);
        }
      };
      
      reader.onerror = (error) => {
        console.error('File reader error:', error);
        toast.error('Failed to read image file');
        setAnalyzing(false);
      };
      
      reader.readAsDataURL(selectedImage);
    } catch (error) {
      console.error('Error analyzing image:', error);
      toast.error('Analysis failed. Please try again.');
      setAnalyzing(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'bg-red-500';
      case 'medium':
        return 'bg-amber-500';
      case 'low':
        return 'bg-blue-500';
      default:
        return 'bg-zinc-600';
    }
  };

  const getSafetyScoreColor = (score) => {
    switch (score?.toLowerCase()) {
      case 'safe':
        return 'text-green-500';
      case 'caution':
        return 'text-amber-500';
      case 'danger':
        return 'text-red-500';
      default:
        return 'text-zinc-400';
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950">
      <Toaster position="top-right" theme="dark" />
      
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-black tracking-tight text-zinc-100 font-chivo">
                WAREHOUSE VISION AI
              </h1>
              <p className="text-sm text-zinc-400 mt-1 font-manrope">
                Autonomous Intralogistics Intelligence System
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="border-amber-500 text-amber-500 px-3 py-1">
                <Activity className="w-3 h-3 mr-1" />
                OPERATIONAL
              </Badge>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Upload Zone - Main Area */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* Upload Card */}
            <Card className="bg-zinc-900 border-zinc-800 overflow-hidden corner-accent">
              <div className="p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-amber-500/10 rounded">
                    <Scan className="w-5 h-5 text-amber-500" />
                  </div>
                  <h2 className="text-xl font-bold text-zinc-100 font-chivo tracking-tight">
                    VISION ANALYSIS
                  </h2>
                </div>

                {/* Drag & Drop Zone */}
                <div
                  data-testid="upload-dropzone"
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`relative border-2 border-dashed rounded-sm p-12 text-center transition-all ${
                    isDragging
                      ? 'border-amber-500 bg-amber-500/5'
                      : 'border-zinc-700 hover:border-zinc-600 bg-zinc-950/50'
                  }`}
                >
                  {isDragging && <div className="scanning-line" />}
                  
                  {!imagePreview ? (
                    <div className="space-y-4">
                      <div className="flex justify-center">
                        <Upload className="w-16 h-16 text-zinc-600" />
                      </div>
                      <div>
                        <p className="text-lg font-semibold text-zinc-300 mb-2">
                          Drop warehouse image or click to upload
                        </p>
                        <p className="text-sm text-zinc-500">
                          Supported: JPEG, PNG, WEBP
                        </p>
                      </div>
                      <input
                        type="file"
                        id="file-input"
                        accept="image/*"
                        onChange={handleFileInput}
                        className="hidden"
                      />
                      <label htmlFor="file-input">
                        <div
                          className="inline-flex items-center justify-center rounded-sm text-sm font-bold uppercase tracking-wider bg-amber-500 hover:bg-amber-600 text-white px-6 py-3 cursor-pointer transition-colors"
                          data-testid="file-upload-button"
                        >
                          SELECT IMAGE
                        </div>
                      </label>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="image-preview mx-auto rounded border border-zinc-700"
                      />
                      <div className="flex gap-3 justify-center">
                        <Button
                          onClick={() => {
                            setSelectedImage(null);
                            setImagePreview(null);
                            setAnalysis(null);
                          }}
                          variant="outline"
                          className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
                        >
                          Clear
                        </Button>
                        <Button
                          onClick={analyzeImage}
                          disabled={analyzing}
                          className="bg-amber-500 hover:bg-amber-600 text-white font-bold uppercase tracking-wider rounded-sm glow-amber"
                          data-testid="analyze-button"
                        >
                          {analyzing ? (
                            <>
                              <Activity className="w-4 h-4 mr-2 animate-spin" />
                              ANALYZING...
                            </>
                          ) : (
                            <>
                              <Scan className="w-4 h-4 mr-2" />
                              ANALYZE
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </Card>

            {/* Analysis Results */}
            {analysis && (
              <Card className="bg-zinc-900 border-zinc-800" data-testid="analysis-results">
                <div className="p-8">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold text-zinc-100 font-chivo tracking-tight">
                      DETECTION RESULTS
                    </h3>
                    <div className="flex items-center gap-2">
                      <Shield className={`w-5 h-5 ${getSafetyScoreColor(analysis.overall_safety_score)}`} />
                      <span className={`font-bold font-jetbrains ${getSafetyScoreColor(analysis.overall_safety_score)}`}>
                        {analysis.overall_safety_score?.toUpperCase()}
                      </span>
                    </div>
                  </div>

                  <p className="text-zinc-400 mb-6">{analysis.summary}</p>

                  <div className="space-y-3">
                    {analysis.detected_items?.map((item, index) => (
                      <Card
                        key={index}
                        className={`bg-zinc-950 border-zinc-800 p-4 ${
                          item.category === 'hazard' ? 'border-l-4 border-l-red-500' : 'border-l-4 border-l-blue-500'
                        }`}
                        data-testid={`detected-item-${index}`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              {item.category === 'hazard' ? (
                                <AlertTriangle className="w-5 h-5 text-red-500" />
                              ) : (
                                <Package className="w-5 h-5 text-blue-500" />
                              )}
                              <h4 className="font-bold text-zinc-100">{item.name}</h4>
                              <Badge className={`${getPriorityColor(item.priority)} text-white text-xs uppercase`}>
                                {item.priority}
                              </Badge>
                            </div>
                            <p className="text-sm text-zinc-400 mb-2">{item.description}</p>
                            <div className="flex items-center gap-4 text-xs text-zinc-500">
                              <span className="font-jetbrains">Confidence: {item.confidence}</span>
                              {item.location && <span>Location: {item.location}</span>}
                            </div>
                          </div>
                        </div>
                        <Separator className="my-3 bg-zinc-800" />
                        <div className="flex items-start gap-2">
                          <ChevronRight className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-amber-500 font-medium">
                            <span className="text-zinc-500">Action:</span> {item.action}
                          </p>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              </Card>
            )}
          </div>

          {/* Sidebar - Stats & History */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Stats Card */}
            <Card className="bg-zinc-900 border-zinc-800">
              <div className="p-6">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-4 h-4 text-blue-500" />
                  <h3 className="text-sm font-bold text-zinc-300 uppercase tracking-wider font-chivo">
                    System Statistics
                  </h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-zinc-400 text-sm">Total Analyses</span>
                    <span className="font-bold font-jetbrains text-zinc-100">{stats?.total_analyses || 0}</span>
                  </div>
                  <Separator className="bg-zinc-800" />
                  <div className="flex justify-between items-center">
                    <span className="text-zinc-400 text-sm">Safe</span>
                    <span className="font-bold font-jetbrains text-green-500">{stats?.safe_count || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-zinc-400 text-sm">Caution</span>
                    <span className="font-bold font-jetbrains text-amber-500">{stats?.caution_count || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-zinc-400 text-sm">Danger</span>
                    <span className="font-bold font-jetbrains text-red-500">{stats?.danger_count || 0}</span>
                  </div>
                </div>
              </div>
            </Card>

            {/* History Card */}
            <Card className="bg-zinc-900 border-zinc-800">
              <div className="p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Clock className="w-4 h-4 text-blue-500" />
                  <h3 className="text-sm font-bold text-zinc-300 uppercase tracking-wider font-chivo">
                    Recent Analyses
                  </h3>
                </div>
                <ScrollArea className="h-[400px] pr-4">
                  <div className="space-y-3">
                    {history.length === 0 ? (
                      <p className="text-sm text-zinc-500 text-center py-8">No analyses yet</p>
                    ) : (
                      history.map((item, index) => (
                        <Card
                          key={item.id}
                          className="bg-zinc-950 border-zinc-800 p-3 hover:border-zinc-700 transition-colors cursor-pointer"
                          onClick={() => setAnalysis(item)}
                          data-testid={`history-item-${index}`}
                        >
                          <div className="flex items-start justify-between gap-2 mb-2">
                            <span className="text-xs text-zinc-400 truncate flex-1">{item.image_name}</span>
                            <Badge className={`${getPriorityColor(item.detected_items?.[0]?.priority)} text-white text-xs`}>
                              {item.detected_items?.length || 0}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className={`text-xs font-bold ${getSafetyScoreColor(item.overall_safety_score)}`}>
                              {item.overall_safety_score}
                            </span>
                            <span className="text-xs text-zinc-500 font-jetbrains">
                              {new Date(item.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                        </Card>
                      ))
                    )}
                  </div>
                </ScrollArea>
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;