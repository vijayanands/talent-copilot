import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

const predefinedPrompts = [
  { value: 'self_appraisal', label: 'Generate a self appraisal for me' },
  { value: 'endorsements', label: 'Show me the endorsements I have' },
  { value: 'career', label: 'Show me my current career trajectory information' },
  { value: 'skills', label: 'I would like to manage my skills' },
  { value: 'learning', label: 'I would like to manage my learning opportunities' },
  { value: 'productivity', label: 'I would like to get a picture of my productivity' },
  { value: 'custom', label: 'I just want to ask a custom question' }
];

const ConversationalAIDashboard = ({ user, llm_choice }) => {
  const [selectedPrompt, setSelectedPrompt] = useState('');
  const [customQuestion, setCustomQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handlePromptChange = (value) => {
    setSelectedPrompt(value);
    if (value !== 'custom') {
      setCustomQuestion('');
    }
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const question = selectedPrompt === 'custom' ? customQuestion : selectedPrompt;
      const result = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, user, llm_choice }),
      });
      const data = await result.json();
      setResponse(data.response);
    } catch (error) {
      console.error('Error:', error);
      setResponse('An error occurred while processing your request.');
    }
    setIsLoading(false);
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <h2 className="text-2xl font-bold">
          Good morning, {user.first_name || user.email.split('@')[0]}
        </h2>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Select onValueChange={handlePromptChange} value={selectedPrompt}>
            <SelectTrigger>
              <SelectValue placeholder="Select a prompt or question" />
            </SelectTrigger>
            <SelectContent>
              {predefinedPrompts.map((prompt) => (
                <SelectItem key={prompt.value} value={prompt.value}>
                  {prompt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          {selectedPrompt === 'custom' && (
            <Input
              placeholder="Enter your custom question here"
              value={customQuestion}
              onChange={(e) => setCustomQuestion(e.target.value)}
            />
          )}
          
          <Button onClick={handleSubmit} disabled={isLoading || (!selectedPrompt && !customQuestion)}>
            {isLoading ? 'Processing...' : 'Submit'}
          </Button>
          
          {response && (
            <div className="mt-4 p-4 bg-gray-100 rounded-md">
              <h3 className="font-semibold mb-2">Response:</h3>
              <p>{response}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ConversationalAIDashboard;
