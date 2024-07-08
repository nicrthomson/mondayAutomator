import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';

const Dashboard = () => {
  const [apiKey, setApiKey] = useState('');
  const [boardId, setBoardId] = useState('');
  const [itemName, setItemName] = useState('');
  const [status, setStatus] = useState('');
  const [text, setText] = useState('');
  const [itemId, setItemId] = useState('');
  const [columnId, setColumnId] = useState('');
  const [columnValue, setColumnValue] = useState('');
  const [items, setItems] = useState([]);
  const [responseMessage, setResponseMessage] = useState('');
  const [activeTab, setActiveTab] = useState('boardStarter');
  const router = useRouter();
  const [prompt, setPrompt] = useState('');
  const [workspaceId, setWorkspaceId] = useState('');

  useEffect(() => {
    const checkLogin = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:5000/auth/check', {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        });
        if (response.status !== 200) {
          router.push('/login');
        }
      } catch (error) {
        router.push('/login');
      }
    };
    checkLogin();
  }, [router]);

  const fetchItems = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get_items', {
        headers: {
          'Authorization': apiKey,
          'Board-ID': boardId
        },
        withCredentials: true
      });
      setItems(response.data.data.boards[0].items);
    } catch (error) {
      console.error('There was an error fetching the items!', error);
    }
  };

  useEffect(() => {
    if (apiKey && boardId) {
      fetchItems();
    }
  }, [apiKey, boardId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/process_prompt', { prompt, workspaceId }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log('Board created successfully:', response.data);
      setResponseMessage('Board created successfully!');
    } catch (error) {
      console.error('There was an error processing the prompt!', error);
      setResponseMessage('Error creating board. Please try again.');
    }
  };

  const handleCreateItem = async () => {
    try {
      if (!itemName || !status || !text) {
        setResponseMessage('Please fill all the fields');
        return;
      }
      const payload = {
        item_name: itemName,
        column_values: JSON.stringify({ status, text })
      };
      console.log('Payload for create_item:', payload);
      const response = await axios.post('http://localhost:5000/create_item', payload, {
        headers: {
          'Authorization': apiKey,
          'Board-ID': boardId,
          'Content-Type': 'application/json'
        },
        withCredentials: true
      });
      if (response.status === 200) {
        setResponseMessage('Item created successfully!');
        fetchItems();
      } else {
        setResponseMessage('Failed to create item.');
      }
    } catch (error) {
      setResponseMessage('There was an error creating the item!');
      console.error(error);
    }
  };

  const handleUpdateItem = async () => {
    try {
      const payload = {
        item_id: itemId,
        column_id: columnId,
        value: columnValue
      };
      console.log('Payload for update_item:', payload);
      const response = await axios.post('http://localhost:5000/update_item', payload, {
        headers: {
          'Authorization': apiKey,
          'Board-ID': boardId,
          'Content-Type': 'application/json'
        },
        withCredentials: true
      });
      if (response.status === 200) {
        setResponseMessage('Item updated successfully!');
        fetchItems();
      } else {
        setResponseMessage('Failed to update item.');
      }
    } catch (error) {
      setResponseMessage('There was an error updating the item!');
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <img className="h-8 w-auto" src="/logo.svg" alt="" />
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <button
                  onClick={() => setActiveTab('boardStarter')}
                  className={`${
                    activeTab === 'boardStarter'
                      ? 'border-gray-900 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                >
                  Board Starter
                </button>
                <button
                  onClick={() => setActiveTab('boardEditor')}
                  className={`${
                    activeTab === 'boardEditor'
                      ? 'border-gray-900 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                >
                  Board Editor
                </button>
                <button
                  onClick={() => setActiveTab('automations')}
                  className={`${
                    activeTab === 'automations'
                      ? 'border-gray-900 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                >
                  Automations
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === 'boardStarter' && (
          <div className="bg-white shadow">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Create Board from Prompt</h3>
              <div className="mt-5">
                <form onSubmit={handleSubmit}>
                  <div className="mb-6">
                    <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-1">
                      Prompt
                    </label>
                    <textarea
                      id="prompt"
                      rows={4}
                      className="shadow-sm mt-1 block w-full text-base border-gray-300 border-2 pl-2 py-2 focus:ring-gray-500 focus:border-gray-500"
                      placeholder="Enter your prompt"
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                    />
                  </div>
                  <div className="mb-6">
                    <label htmlFor="workspaceId" className="block text-sm font-medium text-gray-700 mb-1">
                      Workspace ID
                    </label>
                    <input
                      type="text"
                      id="workspaceId"
                      className="shadow-sm mt-1 block w-full text-base border-gray-300 border-2 pl-2 py-2 focus:ring-gray-500 focus:border-gray-500"
                      placeholder="Enter workspace ID"
                      value={workspaceId}
                      onChange={(e) => setWorkspaceId(e.target.value)}
                    />
                  </div>
                  <button
                    type="submit"
                    className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium shadow-sm text-white bg-gray-900 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                  >
                    Create Board
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'boardEditor' && (
          <div className="bg-white shadow">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Board Editor</h3>
              <div className="mt-5 space-y-6">
                <div>
                  <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-1">
                    API Key
                  </label>
                  <input
                    type="text"
                    id="apiKey"
                    className="mt-1 block w-full text-base border-gray-300 border-2 pl-2 py-2 shadow-sm focus:ring-gray-500 focus:border-gray-500"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                  />
                </div>
                <div>
                  <label htmlFor="boardId" className="block text-sm font-medium text-gray-700 mb-1">
                    Board ID
                  </label>
                  <input
                    type="text"
                    id="boardId"
                    className="mt-1 block w-full text-base border-gray-300 border-2 pl-2 py-2 shadow-sm focus:ring-gray-500 focus:border-gray-500"
                    value={boardId}
                    onChange={(e) => setBoardId(e.target.value)}
                  />
                </div>
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-2">Create New Item</h4>
                  <div className="space-y-3">
                    <input
                      type="text"
                      placeholder="Item Name"
                      className="block w-full text-base border-gray-300 border-2 pl-2 py-2 shadow-sm focus:ring-gray-500 focus:border-gray-500"
                      value={itemName}
                      onChange={(e) => setItemName(e.target.value)}
                    />
                    <input
                      type="text"
                      placeholder="Status"
                      className="block w-full text-base border-gray-300 border-2 pl-2 py-2 shadow-sm focus:ring-gray-500 focus:border-gray-500"
                      value={status}
                      onChange={(e) => setStatus(e.target.value)}
                    />
                    <input
                      type="text"
                      placeholder="Text"
                      className="block w-full text-base border-gray-300 border-2 pl-2 py-2 shadow-sm focus:ring-gray-500 focus:border-gray-500"
                      value={text}
                      onChange={(e) => setText(e.target.value)}
                    />
                    <button
                      onClick={handleCreateItem}
                      className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium shadow-sm text-white bg-gray-900 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                    >
                      Create Item
                    </button>
                  </div>
                </div>
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-2">Update Item Status</h4>
                  <div className="space-y-3">
                    <input
                      type="text"
                      placeholder="Item ID"
                      className="block w-full text-base border-gray-300 border-2 pl-2 py-2 shadow-sm focus:ring-gray-500 focus:border-gray-500"
                      value={itemId}
                      onChange={(e) => setItemId(e.target.value)}
                    />
                    <input
                      type="text"
                      placeholder="Column ID"
                      className="block w-full text-base border-gray-300 border-2 pl-2 py-2 shadow-sm focus:ring-gray-500 focus:border-gray-500"
                      value={columnId}
                      onChange={(e) => setColumnId(e.target.value)}
                    />
                    <input
                      type="text"
                      placeholder="Column Value"
                      className="block w-full text-base border-gray-300 border-2 pl-2 py-2 shadow-sm focus:ring-gray-500 focus:border-gray-500"
                      value={columnValue}
                      onChange={(e) => setColumnValue(e.target.value)}
                    />
                    <button
                      onClick={handleUpdateItem}
                      className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium shadow-sm text-white bg-gray-900 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                    >
                      Update Item
                    </button>
                  </div>
                </div>
              </div>
              {responseMessage && (
                <div className="mt-4 p-4 bg-green-100">
                  <p className="text-green-700">{responseMessage}</p>
                </div>
              )}
              <div className="mt-6">
                <h4 className="text-md font-medium text-gray-900">Items</h4>
                <ul className="mt-2 divide-y divide-gray-200">
                  {items.map(item => (
                    <li key={item.id} className="py-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-900">{item.name} - {item.column_values.find(col => col.id === 'status')?.text}</span>
                        <button
                          onClick={() => {
                            setItemId(item.id);
                            setColumnId('status');
                            setColumnValue('Done');
                            handleUpdateItem();
                          }}
                          className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                        >
                          Mark as Done
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'automations' && (
          <div className="bg-white shadow">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Automations</h3>
              <div className="mt-5">
                <p>Automations feature coming soon!</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;