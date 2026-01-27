"""
Enhanced React/Frontend Advisor Assistant

Comprehensive React and frontend best practices covering:
- React 18 features (concurrent rendering, Suspense, transitions)
- React Server Components (RSC)
- Next.js 14 patterns (App Router, Server Actions)
- State management (Redux, Zustand, Jotai, Recoil)
- Data fetching (React Query, SWR)
- Performance optimization (memo, useMemo, useCallback)
- Error boundaries and Suspense boundaries
- Testing patterns (React Testing Library)

References:
- React Documentation: https://react.dev/
- Next.js Documentation: https://nextjs.org/docs
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class ReactFinding(BaseModel):
    """Structured React finding output"""

    finding_id: str = Field(..., description="Unique identifier (REACT-001, etc.)")
    title: str = Field(..., description="Brief title of the issue")
    severity: str = Field(..., description="CRITICAL/HIGH/MEDIUM/LOW")
    category: str = Field(..., description="Performance/Patterns/State/Hooks/Testing")

    component: str = Field(default="", description="Affected component")
    current_code: str = Field(default="", description="Current code")
    improved_code: str = Field(default="", description="Improved code")

    performance_impact: str = Field(default="", description="Performance impact")
    explanation: str = Field(default="", description="Why this matters")

    tools: List[Dict[str, str]] = Field(default_factory=list)
    remediation: Dict[str, str] = Field(default_factory=dict)


class EnhancedReactAssistant:
    """Enhanced React/Frontend Advisor"""

    def __init__(self):
        self.name = "Enhanced React/Frontend Advisor"
        self.version = "2.0.0"
        self.standards = ["React 18", "Next.js 14", "Web Vitals"]

    # =========================================================================
    # REACT 18 FEATURES
    # =========================================================================

    @staticmethod
    def react_18_features() -> Dict[str, Any]:
        """React 18 new features and patterns"""
        return {
            "concurrent_rendering": """
// React 18 Concurrent Features

// useTransition - Mark updates as non-urgent
function SearchResults() {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    // Urgent: Update input immediately
    setQuery(e.target.value);

    // Non-urgent: Can be interrupted
    startTransition(() => {
      setSearchResults(filterData(e.target.value));
    });
  };

  return (
    <>
      <input value={query} onChange={handleChange} />
      {isPending ? <Spinner /> : <Results />}
    </>
  );
}
            """,
            "suspense_data": """
// Suspense for Data Fetching
function ProfilePage({ userId }) {
  return (
    <Suspense fallback={<ProfileSkeleton />}>
      <ProfileDetails userId={userId} />
      <Suspense fallback={<PostsSkeleton />}>
        <ProfilePosts userId={userId} />
      </Suspense>
    </Suspense>
  );
}

// With React Query
function ProfileDetails({ userId }) {
  const { data } = useSuspenseQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });

  return <div>{data.name}</div>;
}
            """,
            "use_deferred_value": """
// useDeferredValue - Defer re-rendering of expensive components
function SearchPage() {
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);

  return (
    <>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      {/* This re-renders with delay, keeping UI responsive */}
      <SlowList query={deferredQuery} />
    </>
  );
}
            """,
        }

    # =========================================================================
    # SERVER COMPONENTS
    # =========================================================================

    @staticmethod
    def server_components() -> Dict[str, Any]:
        """React Server Components (RSC) patterns"""
        return {
            "server_vs_client": """
// Server Component (default in Next.js App Router)
// - Can't use hooks (useState, useEffect)
// - Can't use browser APIs
// - Can fetch data directly
// - Smaller bundle size

// app/page.tsx (Server Component)
async function Page() {
  const data = await fetch('https://api.example.com/data');
  const posts = await data.json();

  return (
    <div>
      {posts.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
      <LikeButton /> {/* Client Component */}
    </div>
  );
}

// Client Component - add 'use client' directive
// components/LikeButton.tsx
'use client';

import { useState } from 'react';

export function LikeButton() {
  const [liked, setLiked] = useState(false);

  return (
    <button onClick={() => setLiked(!liked)}>
      {liked ? '❤️' : '🤍'}
    </button>
  );
}
            """,
            "patterns": """
// Pattern: Server Component fetches, Client Component renders interactively

// Server Component
async function ProductPage({ id }) {
  const product = await getProduct(id);

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      {/* Client Component for interactivity */}
      <AddToCartButton productId={id} price={product.price} />
    </div>
  );
}

// Pass serializable props to Client Components
// ❌ BAD: Passing functions or non-serializable objects
// ✅ GOOD: Pass primitive values or plain objects
            """,
        }

    # =========================================================================
    # PERFORMANCE OPTIMIZATION
    # =========================================================================

    @staticmethod
    def performance_optimization() -> Dict[str, Any]:
        """React performance best practices"""
        return {
            "memo": {
                "bad": """
// BAD: Component re-renders on every parent render
function ExpensiveList({ items, onSelect }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id} onClick={() => onSelect(item)}>
          {item.name}
        </li>
      ))}
    </ul>
  );
}
                """,
                "good": """
// GOOD: Memoized component
const ExpensiveList = memo(function ExpensiveList({ items, onSelect }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id} onClick={() => onSelect(item)}>
          {item.name}
        </li>
      ))}
    </ul>
  );
});

// Parent must also memoize callback
function Parent() {
  const [items, setItems] = useState([]);

  // BAD: New function on every render
  // const handleSelect = (item) => console.log(item);

  // GOOD: Memoized callback
  const handleSelect = useCallback((item) => {
    console.log(item);
  }, []);

  return <ExpensiveList items={items} onSelect={handleSelect} />;
}
                """,
            },
            "use_memo": """
// useMemo for expensive calculations
function DataGrid({ data, filter }) {
  // BAD: Filters on every render
  // const filteredData = data.filter(item => item.status === filter);

  // GOOD: Only recalculates when data or filter changes
  const filteredData = useMemo(
    () => data.filter(item => item.status === filter),
    [data, filter]
  );

  return <Table data={filteredData} />;
}
            """,
            "virtualization": """
// For large lists, use virtualization
import { FixedSizeList } from 'react-window';

function VirtualizedList({ items }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>
          {items[index].name}
        </div>
      )}
    </FixedSizeList>
  );
}
// Renders only visible items (~20) instead of all 10,000
            """,
        }

    # =========================================================================
    # STATE MANAGEMENT
    # =========================================================================

    @staticmethod
    def state_management() -> Dict[str, Any]:
        """State management comparison and patterns"""
        return {
            "when_to_use": {
                "local_state": "Component-specific UI state (form inputs, toggles)",
                "context": "Theme, auth, small global state (avoid for frequent updates)",
                "zustand": "Simple global state, minimal boilerplate",
                "redux_toolkit": "Complex state with devtools, middleware, large teams",
                "react_query": "Server state (caching, refetching, mutations)",
            },
            "zustand_example": """
// Zustand - Simple and performant
import { create } from 'zustand';

const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
}));

function Counter() {
  const { count, increment } = useStore();
  return <button onClick={increment}>{count}</button>;
}
            """,
            "react_query": """
// React Query for server state
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function UserProfile({ userId }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (isLoading) return <Spinner />;
  if (error) return <Error message={error.message} />;

  return <div>{data.name}</div>;
}

// Mutations with optimistic updates
function LikeButton({ postId }) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => likePost(postId),
    onMutate: async () => {
      // Optimistic update
      await queryClient.cancelQueries(['post', postId]);
      const previous = queryClient.getQueryData(['post', postId]);
      queryClient.setQueryData(['post', postId], old => ({
        ...old,
        likes: old.likes + 1,
      }));
      return { previous };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      queryClient.setQueryData(['post', postId], context.previous);
    },
  });

  return <button onClick={() => mutation.mutate()}>Like</button>;
}
            """,
        }

    # =========================================================================
    # ERROR HANDLING
    # =========================================================================

    @staticmethod
    def error_handling() -> Dict[str, Any]:
        """Error boundaries and error handling patterns"""
        return {
            "error_boundary": """
// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log to error reporting service
    logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<ErrorPage />}>
  <App />
</ErrorBoundary>
            """,
            "react_error_boundary": """
// Using react-error-boundary library
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

<ErrorBoundary
  FallbackComponent={ErrorFallback}
  onReset={() => window.location.reload()}
  onError={(error, info) => logError(error, info)}
>
  <App />
</ErrorBoundary>
            """,
        }

    # =========================================================================
    # NEXT.JS PATTERNS
    # =========================================================================

    @staticmethod
    def nextjs_patterns() -> Dict[str, Any]:
        """Next.js 14+ App Router patterns"""
        return {
            "app_router_structure": '''
// Next.js 14 App Router file structure
app/
├── layout.tsx           // Root layout (required)
├── page.tsx             // Home page (/)
├── loading.tsx          // Loading UI
├── error.tsx            // Error UI
├── not-found.tsx        // 404 page
├── global-error.tsx     // Global error boundary
├── dashboard/
│   ├── layout.tsx       // Dashboard layout
│   ├── page.tsx         // Dashboard page (/dashboard)
│   └── settings/
│       └── page.tsx     // Settings page (/dashboard/settings)
├── api/
│   └── users/
│       └── route.ts     // API route (/api/users)
└── (marketing)/         // Route group (no URL segment)
    ├── about/
    │   └── page.tsx     // About page (/about)
    └── blog/
        └── page.tsx     // Blog page (/blog)
            ''',
            "server_actions": '''
// Server Actions (Next.js 14+)
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';

export async function createUser(formData: FormData) {
  // This runs on the server
  const name = formData.get('name');
  const email = formData.get('email');

  // Validate
  if (!name || !email) {
    return { error: 'Name and email required' };
  }

  // Database operation
  const user = await db.user.create({
    data: { name, email }
  });

  // Revalidate cache
  revalidatePath('/users');

  // Redirect
  redirect(`/users/${user.id}`);
}

// app/users/new/page.tsx
import { createUser } from '@/app/actions';

export default function NewUserPage() {
  return (
    <form action={createUser}>
      <input name="name" placeholder="Name" required />
      <input name="email" type="email" placeholder="Email" required />
      <button type="submit">Create User</button>
    </form>
  );
}

// With useFormState for error handling
'use client'
import { useFormState } from 'react-dom';
import { createUser } from '@/app/actions';

function CreateUserForm() {
  const [state, formAction] = useFormState(createUser, null);

  return (
    <form action={formAction}>
      <input name="name" placeholder="Name" />
      <input name="email" type="email" placeholder="Email" />
      {state?.error && <p className="error">{state.error}</p>}
      <SubmitButton />
    </form>
  );
}

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Creating...' : 'Create User'}
    </button>
  );
}
            ''',
            "parallel_routes": '''
// Parallel Routes - render multiple pages in the same layout
app/
├── layout.tsx
├── page.tsx
├── @team/
│   └── page.tsx         // Parallel route
├── @analytics/
│   └── page.tsx         // Another parallel route
└── @analytics/
    └── loading.tsx      // Loading state for analytics

// layout.tsx
export default function Layout({
  children,
  team,
  analytics
}: {
  children: React.ReactNode;
  team: React.ReactNode;
  analytics: React.ReactNode;
}) {
  return (
    <div>
      {children}
      <aside>
        {team}
        {analytics}
      </aside>
    </div>
  );
}
            ''',
            "intercepting_routes": '''
// Intercepting Routes - show modal while preserving URL
app/
├── feed/
│   └── page.tsx
├── photo/
│   └── [id]/
│       └── page.tsx       // Full photo page
└── @modal/
    └── (.)photo/
        └── [id]/
            └── page.tsx   // Modal view (intercepts from feed)

// (.) intercepts same level
// (..) intercepts one level up
// (...) intercepts from root

// Example: Instagram-like feed with modal photo view
// Clicking photo in feed shows modal
// Direct URL to /photo/123 shows full page
            ''',
            "streaming": '''
// Streaming with Suspense
// app/dashboard/page.tsx
import { Suspense } from 'react';
import { SlowComponent } from './SlowComponent';

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* This streams in as it becomes ready */}
      <Suspense fallback={<LoadingSkeleton />}>
        <SlowComponent />
      </Suspense>
    </div>
  );
}

// loading.tsx provides automatic Suspense boundary
// app/dashboard/loading.tsx
export default function Loading() {
  return <DashboardSkeleton />;
}
            ''',
        }

    # =========================================================================
    # TESTING PATTERNS
    # =========================================================================

    @staticmethod
    def testing_patterns() -> Dict[str, Any]:
        """React testing best practices"""
        return {
            "component_testing": '''
// React Testing Library - test behavior, not implementation
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// BAD: Testing implementation details
test('bad - tests implementation', () => {
  const { container } = render(<Counter />);
  expect(container.querySelector('.count')).toHaveTextContent('0');
  // Breaks if class name changes
});

// GOOD: Testing user-visible behavior
test('good - tests behavior', async () => {
  const user = userEvent.setup();
  render(<Counter />);

  // Use accessible queries
  expect(screen.getByRole('heading', { name: /count/i })).toHaveTextContent('0');

  // Interact like a user
  await user.click(screen.getByRole('button', { name: /increment/i }));

  expect(screen.getByRole('heading', { name: /count/i })).toHaveTextContent('1');
});

// Testing async operations
test('loads user data', async () => {
  render(<UserProfile userId="123" />);

  // Wait for loading to complete
  expect(screen.getByText(/loading/i)).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByText(/john doe/i)).toBeInTheDocument();
  });
});

// Query priority (most to least preferred):
// 1. getByRole - accessible to everyone
// 2. getByLabelText - form elements
// 3. getByPlaceholderText - input elements
// 4. getByText - non-interactive elements
// 5. getByTestId - last resort
            ''',
            "mocking": '''
// Mocking with Jest and MSW

// Mock API calls with MSW (Mock Service Worker)
// mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/users/:id', (req, res, ctx) => {
    return res(
      ctx.json({
        id: req.params.id,
        name: 'John Doe',
        email: 'john@example.com'
      })
    );
  }),

  rest.post('/api/users', async (req, res, ctx) => {
    const body = await req.json();
    return res(
      ctx.status(201),
      ctx.json({ id: '123', ...body })
    );
  }),

  // Error scenarios
  rest.get('/api/users/error', (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({ error: 'Server error' }));
  }),
];

// setupTests.ts
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Test with MSW
test('displays user data', async () => {
  render(<UserProfile userId="123" />);

  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});

// Override handler for specific test
test('handles error', async () => {
  server.use(
    rest.get('/api/users/:id', (req, res, ctx) => {
      return res(ctx.status(500));
    })
  );

  render(<UserProfile userId="123" />);

  await waitFor(() => {
    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });
});
            ''',
            "custom_hooks_testing": '''
// Testing custom hooks with renderHook
import { renderHook, act } from '@testing-library/react';

// Custom hook
function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);

  const increment = useCallback(() => setCount(c => c + 1), []);
  const decrement = useCallback(() => setCount(c => c - 1), []);
  const reset = useCallback(() => setCount(initialValue), [initialValue]);

  return { count, increment, decrement, reset };
}

// Test
test('useCounter hook', () => {
  const { result } = renderHook(() => useCounter(10));

  expect(result.current.count).toBe(10);

  act(() => {
    result.current.increment();
  });

  expect(result.current.count).toBe(11);

  act(() => {
    result.current.reset();
  });

  expect(result.current.count).toBe(10);
});

// Test with wrapper for context
const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

test('useUser hook', async () => {
  const { result } = renderHook(() => useUser('123'), { wrapper });

  await waitFor(() => {
    expect(result.current.isLoading).toBe(false);
  });

  expect(result.current.data.name).toBe('John Doe');
});
            ''',
        }

    # =========================================================================
    # FORM HANDLING
    # =========================================================================

    @staticmethod
    def form_handling() -> Dict[str, Any]:
        """Form handling patterns with React Hook Form and Zod"""
        return {
            "react_hook_form": '''
// React Hook Form with Zod validation
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// Define schema
const userSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  age: z.number().min(18, 'Must be at least 18'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/[0-9]/, 'Must contain number'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

type UserFormData = z.infer<typeof userSchema>;

function UserForm({ onSubmit }: { onSubmit: (data: UserFormData) => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      name: '',
      email: '',
      age: 18,
    },
  });

  const onSubmitHandler = async (data: UserFormData) => {
    try {
      await onSubmit(data);
      reset();
    } catch (error) {
      // Handle error
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmitHandler)}>
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" {...register('name')} />
        {errors.name && <span className="error">{errors.name.message}</span>}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" {...register('email')} />
        {errors.email && <span className="error">{errors.email.message}</span>}
      </div>

      <div>
        <label htmlFor="age">Age</label>
        <input id="age" type="number" {...register('age', { valueAsNumber: true })} />
        {errors.age && <span className="error">{errors.age.message}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
            ''',
            "field_arrays": '''
// Dynamic form fields with useFieldArray
import { useForm, useFieldArray } from 'react-hook-form';

const orderSchema = z.object({
  items: z.array(z.object({
    productId: z.string(),
    quantity: z.number().min(1),
    price: z.number().min(0),
  })).min(1, 'At least one item required'),
});

function OrderForm() {
  const { control, register, handleSubmit } = useForm({
    resolver: zodResolver(orderSchema),
    defaultValues: {
      items: [{ productId: '', quantity: 1, price: 0 }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {fields.map((field, index) => (
        <div key={field.id}>
          <input {...register(`items.${index}.productId`)} placeholder="Product" />
          <input
            type="number"
            {...register(`items.${index}.quantity`, { valueAsNumber: true })}
          />
          <input
            type="number"
            {...register(`items.${index}.price`, { valueAsNumber: true })}
          />
          <button type="button" onClick={() => remove(index)}>Remove</button>
        </div>
      ))}

      <button type="button" onClick={() => append({ productId: '', quantity: 1, price: 0 })}>
        Add Item
      </button>

      <button type="submit">Submit Order</button>
    </form>
  );
}
            ''',
        }

    # =========================================================================
    # ACCESSIBILITY
    # =========================================================================

    @staticmethod
    def accessibility_patterns() -> Dict[str, Any]:
        """Accessibility (a11y) patterns in React"""
        return {
            "semantic_html": '''
// Use semantic HTML elements
// BAD
<div onClick={handleClick}>Click me</div>

// GOOD - native button behavior
<button onClick={handleClick}>Click me</button>

// BAD - div with role
<div role="navigation">...</div>

// GOOD - semantic nav
<nav aria-label="Main navigation">...</nav>

// Headings - maintain hierarchy
<main>
  <h1>Page Title</h1>
  <section>
    <h2>Section Title</h2>
    <h3>Subsection</h3>
  </section>
</main>
            ''',
            "aria_attributes": '''
// ARIA attributes for enhanced accessibility

// Live regions for dynamic content
function Notification({ message }) {
  return (
    <div role="status" aria-live="polite">
      {message}
    </div>
  );
}

// Progress indicators
function ProgressBar({ progress }) {
  return (
    <div
      role="progressbar"
      aria-valuenow={progress}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label="Upload progress"
    >
      {progress}%
    </div>
  );
}

// Modal dialog
function Modal({ isOpen, onClose, title, children }) {
  return (
    <dialog
      open={isOpen}
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby="modal-description"
    >
      <h2 id="modal-title">{title}</h2>
      <div id="modal-description">{children}</div>
      <button onClick={onClose} aria-label="Close modal">
        ×
      </button>
    </dialog>
  );
}

// Form labels
<label htmlFor="email">Email Address</label>
<input
  id="email"
  type="email"
  aria-describedby="email-hint"
  aria-invalid={hasError}
  aria-errormessage={hasError ? "email-error" : undefined}
/>
<span id="email-hint">We'll never share your email</span>
{hasError && <span id="email-error" role="alert">Invalid email</span>}
            ''',
            "keyboard_navigation": '''
// Keyboard navigation support

// Focus management
import { useRef, useEffect } from 'react';

function SearchModal({ isOpen, onClose }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  // Trap focus inside modal
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }

    if (e.key === 'Tab') {
      // Simple focus trap between input and close button
      if (e.shiftKey && document.activeElement === inputRef.current) {
        e.preventDefault();
        closeButtonRef.current?.focus();
      } else if (!e.shiftKey && document.activeElement === closeButtonRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    }
  };

  return (
    <div role="dialog" onKeyDown={handleKeyDown}>
      <input ref={inputRef} type="search" placeholder="Search..." />
      <button ref={closeButtonRef} onClick={onClose}>Close</button>
    </div>
  );
}

// Skip link for keyboard users
function Layout({ children }) {
  return (
    <>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <header>...</header>
      <main id="main-content" tabIndex={-1}>
        {children}
      </main>
    </>
  );
}
            ''',
            "testing_a11y": '''
// Testing accessibility with jest-axe
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('form is accessible', async () => {
  const { container } = render(<UserForm />);

  const results = await axe(container);

  expect(results).toHaveNoViolations();
});

// Cypress with cypress-axe
describe('Accessibility', () => {
  beforeEach(() => {
    cy.visit('/');
    cy.injectAxe();
  });

  it('has no accessibility violations', () => {
    cy.checkA11y();
  });

  it('has no violations in modal', () => {
    cy.get('button').contains('Open Modal').click();
    cy.checkA11y('.modal');
  });
});
            ''',
        }

    # =========================================================================
    # CODE SPLITTING
    # =========================================================================

    @staticmethod
    def code_splitting() -> Dict[str, Any]:
        """Code splitting and lazy loading patterns"""
        return {
            "lazy_loading": '''
// React.lazy for code splitting
import { lazy, Suspense } from 'react';

// Lazy load component
const Dashboard = lazy(() => import('./Dashboard'));
const Settings = lazy(() => import('./Settings'));

// With named exports
const Analytics = lazy(() =>
  import('./Analytics').then(module => ({ default: module.Analytics }))
);

function App() {
  return (
    <Router>
      <Suspense fallback={<PageSkeleton />}>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Suspense>
    </Router>
  );
}
            ''',
            "prefetching": '''
// Prefetch routes on hover
import { lazy, Suspense, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';

// Create lazy component that can be prefetched
const Settings = lazy(() => import('./Settings'));

// Prefetch function
const prefetchSettings = () => {
  import('./Settings');
};

function Navigation() {
  return (
    <nav>
      <Link
        to="/settings"
        onMouseEnter={prefetchSettings}  // Prefetch on hover
        onFocus={prefetchSettings}        // Prefetch on focus
      >
        Settings
      </Link>
    </nav>
  );
}

// With React Query prefetching
import { useQueryClient } from '@tanstack/react-query';

function UserList() {
  const queryClient = useQueryClient();

  const prefetchUser = (userId: string) => {
    queryClient.prefetchQuery({
      queryKey: ['user', userId],
      queryFn: () => fetchUser(userId),
      staleTime: 60000, // 1 minute
    });
  };

  return (
    <ul>
      {users.map(user => (
        <li
          key={user.id}
          onMouseEnter={() => prefetchUser(user.id)}
        >
          <Link to={`/users/${user.id}`}>{user.name}</Link>
        </li>
      ))}
    </ul>
  );
}
            ''',
            "bundle_analysis": '''
// Analyze bundle size
// package.json
{
  "scripts": {
    "analyze": "ANALYZE=true npm run build"
  }
}

// next.config.js (Next.js)
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // Next.js config
});

// Vite
import { visualizer } from 'rollup-plugin-visualizer';

export default {
  plugins: [
    visualizer({
      open: true,
      gzipSize: true,
    }),
  ],
};
            ''',
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        component: str,
        current_code: str,
        improved_code: str,
        performance_impact: str = "",
    ) -> ReactFinding:
        """Generate a structured finding"""
        return ReactFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            component=component,
            current_code=current_code,
            improved_code=improved_code,
            performance_impact=performance_impact,
            tools=self.get_tool_recommendations(),
            remediation={
                "effort": "LOW" if severity == "LOW" else "MEDIUM",
                "priority": severity
            },
        )

    @staticmethod
    def get_tool_recommendations() -> List[Dict[str, str]]:
        """Get recommended tools for React development"""
        return [
            {
                "name": "React DevTools",
                "command": "Install Chrome/Firefox extension",
                "description": "Component inspector and Profiler for performance"
            },
            {
                "name": "why-did-you-render",
                "command": "npm install @welldone-software/why-did-you-render",
                "description": "Detect unnecessary re-renders"
            },
            {
                "name": "Bundle Analyzer",
                "command": "npx @next/bundle-analyzer",
                "description": "Visualize bundle composition"
            },
            {
                "name": "Lighthouse",
                "command": "npx lighthouse http://localhost:3000 --view",
                "description": "Performance and accessibility audit"
            },
            {
                "name": "jest-axe",
                "command": "npm install jest-axe",
                "description": "Automated accessibility testing"
            },
            {
                "name": "MSW",
                "command": "npm install msw",
                "description": "API mocking for testing"
            },
        ]


def create_enhanced_react_assistant():
    """Factory function to create Enhanced React/Frontend Assistant"""
    return {
        "name": "Enhanced React/Frontend Advisor",
        "version": "2.0.0",
        "system_prompt": """You are an expert React and frontend development advisor with comprehensive
knowledge of modern React patterns and best practices. Your expertise covers:

REACT 18+ FEATURES:
- Concurrent rendering and automatic batching
- Suspense for data fetching and code splitting
- useTransition and useDeferredValue for non-blocking updates
- Streaming SSR with selective hydration
- React Server Components (RSC)

NEXT.JS 14+ (APP ROUTER):
- App Router file conventions and layouts
- Server Components vs Client Components
- Server Actions for mutations
- Parallel and intercepting routes
- Streaming and loading states
- Metadata API for SEO

STATE MANAGEMENT:
- Built-in React state (useState, useReducer, Context)
- Server state with React Query/TanStack Query
- Client state with Zustand, Jotai, Recoil
- Redux Toolkit for complex state
- When to use which solution

PERFORMANCE OPTIMIZATION:
- React.memo, useMemo, useCallback
- Virtualization for large lists (react-window, react-virtualized)
- Code splitting with React.lazy and Suspense
- Bundle optimization and tree shaking
- Image optimization (next/image)
- Web Vitals (LCP, FID, CLS)

TESTING:
- React Testing Library best practices
- Testing user behavior, not implementation
- MSW for API mocking
- Custom hook testing
- Accessibility testing with jest-axe

FORMS AND VALIDATION:
- React Hook Form for performant forms
- Zod for type-safe validation
- Dynamic form fields with useFieldArray
- Server Actions for form submission

ACCESSIBILITY (A11Y):
- Semantic HTML and ARIA
- Keyboard navigation
- Screen reader support
- Focus management

Analyze React code for anti-patterns and optimization opportunities.
Provide before/after examples with performance impact measurements.

Format findings with severity levels and specific remediation steps.""",
        "assistant_class": EnhancedReactAssistant,
        "finding_model": ReactFinding,
        "domain": "frontend",
        "subdomain": "react",
        "tags": ["react", "nextjs", "frontend", "performance", "javascript", "typescript"],
        "tools": EnhancedReactAssistant.get_tool_recommendations(),
        "capabilities": [
            "performance_optimization",
            "state_management_review",
            "server_components_guidance",
            "testing_patterns",
            "accessibility_audit",
            "code_splitting",
            "form_handling"
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedReactAssistant()
    print(f"=== {assistant.name} v{assistant.version} ===\n")
    print(f"Standards: {', '.join(assistant.standards)}\n")

    # Demonstrate React 18 features
    print("--- React 18 Features ---")
    r18 = assistant.react_18_features()
    print("useTransition: Mark updates as non-urgent")
    print("useDeferredValue: Defer rendering of expensive components")
    print("Suspense: Data fetching and code splitting")

    # Demonstrate Server Components
    print("\n--- React Server Components ---")
    rsc = assistant.server_components()
    print("Server Components: No bundle, direct data access")
    print("Client Components: Interactivity with 'use client'")
    print("Pattern: Server fetches, Client renders interactively")

    # Show performance optimization
    print("\n--- Performance Optimization ---")
    perf = assistant.performance_optimization()
    print("React.memo: Prevent unnecessary re-renders")
    print("useMemo: Cache expensive calculations")
    print("useCallback: Memoize callbacks for child components")
    print("Virtualization: Render only visible list items")

    # Show state management
    print("\n--- State Management ---")
    state = assistant.state_management()
    print("Local: useState for component-specific UI")
    print("Context: Theme, auth (avoid for frequent updates)")
    print("Zustand: Simple global state")
    print("React Query: Server state with caching")

    # Show Next.js patterns
    print("\n--- Next.js 14 Patterns ---")
    nextjs = assistant.nextjs_patterns()
    print("App Router: File-based routing with layouts")
    print("Server Actions: Form mutations without API routes")
    print("Parallel Routes: Multiple pages in same layout")
    print("Streaming: Progressive page loading")

    # Show testing patterns
    print("\n--- Testing Patterns ---")
    testing = assistant.testing_patterns()
    print("React Testing Library: Test behavior, not implementation")
    print("MSW: Mock APIs at network level")
    print("renderHook: Test custom hooks")

    # Show form handling
    print("\n--- Form Handling ---")
    forms = assistant.form_handling()
    print("React Hook Form: Performant, minimal re-renders")
    print("Zod: Type-safe validation with inference")
    print("useFieldArray: Dynamic form fields")

    # Show accessibility patterns
    print("\n--- Accessibility Patterns ---")
    a11y = assistant.accessibility_patterns()
    print("Semantic HTML: Use proper elements")
    print("ARIA: Enhance when needed")
    print("Keyboard: Focus management and navigation")

    # Show code splitting
    print("\n--- Code Splitting ---")
    splitting = assistant.code_splitting()
    print("React.lazy: Dynamic imports")
    print("Prefetching: Load on hover/focus")
    print("Bundle analysis: Optimize imports")

    # Generate sample finding
    print("\n--- Sample Finding ---")
    finding = assistant.generate_finding(
        finding_id="REACT-001",
        title="Missing Memoization Causing Unnecessary Re-renders",
        severity="MEDIUM",
        category="Performance",
        component="ExpensiveList",
        current_code="function ExpensiveList({ items, onSelect }) { ... }",
        improved_code="const ExpensiveList = memo(function ExpensiveList({ items, onSelect }) { ... })",
        performance_impact="Reduces re-renders by ~60% when parent updates"
    )
    print(f"ID: {finding.finding_id}")
    print(f"Title: {finding.title}")
    print(f"Severity: {finding.severity}")
    print(f"Component: {finding.component}")
    print(f"Performance Impact: {finding.performance_impact}")
    print(f"Remediation: {finding.remediation}")

    # Show tool recommendations
    print("\n--- Tool Recommendations ---")
    tools = assistant.get_tool_recommendations()
    for tool in tools[:4]:
        print(f"\n{tool['name']}:")
        print(f"  Command: {tool['command']}")
        print(f"  Description: {tool['description']}")

    # Show factory function output
    print("\n--- Factory Function ---")
    config = create_enhanced_react_assistant()
    print(f"Name: {config['name']}")
    print(f"Version: {config['version']}")
    print(f"Domain: {config['domain']}")
    print(f"Tags: {', '.join(config['tags'])}")
    print(f"Capabilities: {', '.join(config['capabilities'][:3])}...")
