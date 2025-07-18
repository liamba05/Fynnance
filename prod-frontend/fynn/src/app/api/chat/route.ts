import { OpenAIStream, StreamingTextResponse } from "ai";

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    
    // Check authorization (optional for development)
    const authHeader = req.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // For development, we'll stream back a mocked response
    // In production, this would call the backend API
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        // Get the last user message
        const lastUserMessage = messages.filter(m => m.role === 'user').pop()?.content || '';
        
        // Prepare mock response based on user's message
        let response = `I'm Fynn, your financial assistant. `;
        
        if (lastUserMessage.toLowerCase().includes('budget')) {
          response += "I can help you create a budget. Would you like to connect your bank account through Plaid to get started?";
        } else if (lastUserMessage.toLowerCase().includes('invest')) {
          response += "I can provide investment advice based on your financial goals. What are you saving for?";
        } else if (lastUserMessage.toLowerCase().includes('plaid')) {
          response += "Plaid is a secure service that lets you connect your bank accounts to financial apps like Fynn. Would you like to connect your accounts now?";
        } else {
          response += "How can I help with your financial questions today? I can assist with budgeting, investments, and financial planning.";
        }
        
        // Stream the response character by character to simulate typing
        for (let i = 0; i < response.length; i++) {
          const chunk = encoder.encode(response[i]);
          controller.enqueue(chunk);
          await new Promise(resolve => setTimeout(resolve, 20)); // slow down for effect
        }
        controller.close();
      }
    });

    return new StreamingTextResponse(stream);
  } catch (error) {
    console.error('Chat API error:', error);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
