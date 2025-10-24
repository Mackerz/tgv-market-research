"use client";

import { useState, useEffect } from "react";
import { logger } from '@/lib/logger';
import { apiUrl } from '../config/api';
import { surveyService } from '@/lib/api';
import type { QuestionType } from '@/types/survey';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

interface Post {
  id: number;
  title: string;
  content: string | null;
  published: boolean;
  author_id: number;
  created_at: string;
  author: User;
}

export default function Home() {
  const [apiData, setApiData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState<User[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [newUser, setNewUser] = useState({ email: '', username: '', full_name: '' });
  const [newPost, setNewPost] = useState({ title: '', content: '', published: false });
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);

  useEffect(() => {
    // Check API health
    fetch(apiUrl('/api/health'))
      .then(res => res.json())
      .then(data => {
        setApiData(data);
        setLoading(false);
        fetchUsers();
        fetchPosts();
      })
      .catch(err => {
        logger.error('API connection failed:', err);
        setLoading(false);
      });
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch(apiUrl('/api/users/'));
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      logger.error('Failed to fetch users:', error);
    }
  };

  const fetchPosts = async () => {
    try {
      const response = await fetch(apiUrl('/api/posts/'));
      const data = await response.json();
      setPosts(data);
    } catch (error) {
      logger.error('Failed to fetch posts:', error);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(apiUrl('/api/users/'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser),
      });
      if (response.ok) {
        setNewUser({ email: '', username: '', full_name: '' });
        fetchUsers();
      }
    } catch (error) {
      logger.error('Failed to create user:', error);
    }
  };

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUserId) return;
    try {
      const response = await fetch(apiUrl(`/api/users/${selectedUserId}/posts/`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPost),
      });
      if (response.ok) {
        setNewPost({ title: '', content: '', published: false });
        fetchPosts();
      }
    } catch (error) {
      logger.error('Failed to create post:', error);
    }
  };

  const createDemoSurvey = async () => {
    try {
      const demoSurvey = {
        survey_slug: 'demo-survey-' + Date.now(),
        name: 'Complete Survey Demo - All Question Types',
        survey_flow: [
          {
            id: 'q1',
            question: 'What is your favorite color?',
            question_type: 'single' as QuestionType,
            required: true,
            options: ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Other']
          },
          {
            id: 'q2',
            question: 'Which of these activities do you enjoy? (Select all that apply)',
            question_type: 'multi' as QuestionType,
            required: true,
            options: ['Reading', 'Sports', 'Music', 'Gaming', 'Cooking', 'Travel', 'Photography']
          },
          {
            id: 'q3',
            question: 'Please tell us about your hobbies and interests in detail.',
            question_type: 'free_text' as QuestionType,
            required: true
          },
          {
            id: 'q4',
            question: 'Upload a photo that represents your favorite hobby.',
            question_type: 'photo' as QuestionType,
            required: false
          },
          {
            id: 'q5',
            question: 'Record a short video introducing yourself (optional).',
            question_type: 'video' as QuestionType,
            required: false
          }
        ],
        is_active: true
      };

      const survey = await surveyService.createSurvey(demoSurvey);
      alert(`Demo survey created! Visit: /survey/${survey.survey_slug}`);
      // Open in new tab
      window.open(`/survey/${survey.survey_slug}`, '_blank');
    } catch (error) {
      logger.error('Failed to create demo survey:', error);
      alert('Failed to create demo survey');
    }
  };
  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-6 row-start-2 max-w-4xl w-full">
        <div className="text-center mb-4">
          <h1 className="text-3xl font-bold mb-2">FastAPI + PostgreSQL ORM Demo</h1>
          <p className="text-gray-600">SQLAlchemy ORM with Users and Posts</p>
        </div>

        <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg mb-4">
          <h2 className="text-lg font-semibold mb-2">API Connection Status</h2>
          {loading ? (
            <p>Connecting to backend...</p>
          ) : apiData ? (
            <div>
              <p className="text-green-600">✅ Connected to FastAPI backend</p>
              <p>Status: {(apiData as any).status}</p>
              <p>Database: {(apiData as any).database}</p>
            </div>
          ) : (
            <p className="text-red-600">❌ Failed to connect to backend</p>
          )}
        </div>

        {apiData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Create Demo Survey */}
            <div className="md:col-span-3 bg-gradient-to-r from-purple-500 to-pink-500 p-6 rounded-lg text-white">
              <h3 className="text-2xl font-bold mb-4">🚀 Survey System Demo</h3>
              <p className="mb-4">
                Create and test the survey system with a demo survey including all question types.
              </p>
              <button
                onClick={() => createDemoSurvey()}
                className="bg-white text-purple-600 px-6 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
              >
                Create Demo Survey
              </button>
            </div>

            {/* Create User Form */}
            <div className="bg-white dark:bg-gray-900 p-6 rounded-lg border">
              <h3 className="text-xl font-semibold mb-4">Create New User</h3>
              <form onSubmit={handleCreateUser} className="space-y-4">
                <input
                  type="email"
                  placeholder="Email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-700"
                  required
                />
                <input
                  type="text"
                  placeholder="Username"
                  value={newUser.username}
                  onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                  className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-700"
                  required
                />
                <input
                  type="text"
                  placeholder="Full Name (optional)"
                  value={newUser.full_name}
                  onChange={(e) => setNewUser({...newUser, full_name: e.target.value})}
                  className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-700"
                />
                <button
                  type="submit"
                  className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
                >
                  Create User
                </button>
              </form>
            </div>

            {/* Create Post Form */}
            <div className="bg-white dark:bg-gray-900 p-6 rounded-lg border">
              <h3 className="text-xl font-semibold mb-4">Create New Post</h3>
              <form onSubmit={handleCreatePost} className="space-y-4">
                <select
                  value={selectedUserId || ''}
                  onChange={(e) => setSelectedUserId(Number(e.target.value))}
                  className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-700"
                  required
                >
                  <option value="">Select Author</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>{user.username}</option>
                  ))}
                </select>
                <input
                  type="text"
                  placeholder="Post Title"
                  value={newPost.title}
                  onChange={(e) => setNewPost({...newPost, title: e.target.value})}
                  className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-700"
                  required
                />
                <textarea
                  placeholder="Post Content"
                  value={newPost.content}
                  onChange={(e) => setNewPost({...newPost, content: e.target.value})}
                  className="w-full p-2 border rounded h-24 dark:bg-gray-800 dark:border-gray-700"
                />
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newPost.published}
                    onChange={(e) => setNewPost({...newPost, published: e.target.checked})}
                    className="mr-2"
                  />
                  Published
                </label>
                <button
                  type="submit"
                  className="w-full bg-green-500 text-white p-2 rounded hover:bg-green-600"
                  disabled={!selectedUserId}
                >
                  Create Post
                </button>
              </form>
            </div>

            {/* Users List */}
            <div className="bg-white dark:bg-gray-900 p-6 rounded-lg border">
              <h3 className="text-xl font-semibold mb-4">Users ({users.length})</h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {users.map(user => (
                  <div key={user.id} className="p-2 border rounded">
                    <div className="font-semibold">{user.username}</div>
                    <div className="text-sm text-gray-600">{user.email}</div>
                    {user.full_name && <div className="text-sm">{user.full_name}</div>}
                  </div>
                ))}
              </div>
            </div>

            {/* Posts List */}
            <div className="bg-white dark:bg-gray-900 p-6 rounded-lg border">
              <h3 className="text-xl font-semibold mb-4">Posts ({posts.length})</h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {posts.map(post => (
                  <div key={post.id} className="p-2 border rounded">
                    <div className="font-semibold">{post.title}</div>
                    <div className="text-sm text-gray-600">by {post.author.username}</div>
                    {post.content && <div className="text-sm mt-1">{post.content}</div>}
                    <div className="text-xs text-gray-500 mt-1">
                      {post.published ? '✅ Published' : '📝 Draft'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
