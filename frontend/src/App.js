import React, { useState } from 'react';
import {
  Container, Box, TextField, Button, Typography, Paper,
  Tab, Tabs, CircularProgress, Card, CardContent
} from '@mui/material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [stockTicker, setStockTicker] = useState('');
  const [newsQuery, setNewsQuery] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setResult(null);
    setError(null);
  };

  const handleStockSearch = async () => {
    if (!stockTicker) return;
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/stock/${stockTicker}`);
      setResult(response.data.info);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    }
    setLoading(false);
  };

  const handleNewsSearch = async () => {
    if (!newsQuery) return;
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/news/${encodeURIComponent(newsQuery)}`);
      setResult(response.data.news);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    }
    setLoading(false);
  };

  const handleFileUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data.summary);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Financial Assistant
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange} centered>
            <Tab label="Stock Info" />
            <Tab label="Financial News" />
            <Tab label="Document Analysis" />
          </Tabs>
        </Box>

        <Paper sx={{ p: 3, mb: 3 }}>
          {activeTab === 0 && (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                label="Stock Ticker"
                value={stockTicker}
                onChange={(e) => setStockTicker(e.target.value.toUpperCase())}
                placeholder="e.g., AAPL"
              />
              <Button
                variant="contained"
                onClick={handleStockSearch}
                disabled={loading}
              >
                Search
              </Button>
            </Box>
          )}

          {activeTab === 1 && (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                label="News Query"
                value={newsQuery}
                onChange={(e) => setNewsQuery(e.target.value)}
                placeholder="e.g., Tesla earnings"
              />
              <Button
                variant="contained"
                onClick={handleNewsSearch}
                disabled={loading}
              >
                Search
              </Button>
            </Box>
          )}

          {activeTab === 2 && (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
                InputLabelProps={{ shrink: true }}
              />
              <Button
                variant="contained"
                onClick={handleFileUpload}
                disabled={loading || !file}
              >
                Upload & Analyze
              </Button>
            </Box>
          )}
        </Paper>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}

        {result && (
          <Card>
            <CardContent>
              <Typography
                component="pre"
                sx={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  fontFamily: 'monospace'
                }}
              >
                {result}
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>
    </Container>
  );
}

export default App;
