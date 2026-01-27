"""
Enhanced UX Content Writer

Comprehensive UX writing and microcopy guidance covering:
- Button and action text patterns
- Error message frameworks
- Empty states and onboarding
- Loading and progress indicators
- Confirmation dialogs and destructive actions
- Voice and tone guidelines
- Inclusive language standards
- Localization considerations
- Accessibility text (alt text, ARIA labels)

References:
- Nielsen Norman Group UX Writing Guidelines
- Material Design Writing Guidelines
- Apple Human Interface Guidelines
- Microsoft Writing Style Guide
- Mailchimp Content Style Guide
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    """Content issue severity levels"""
    CRITICAL = "critical"  # Blocks user, causes confusion
    HIGH = "high"  # Significant usability impact
    MEDIUM = "medium"  # Noticeable but workaround exists
    LOW = "low"  # Minor polish issue


class ContentCategory(str, Enum):
    """Categories of UX content"""
    BUTTONS = "buttons"
    ERRORS = "errors"
    EMPTY_STATES = "empty_states"
    LOADING = "loading"
    CONFIRMATIONS = "confirmations"
    FORMS = "forms"
    NOTIFICATIONS = "notifications"
    ONBOARDING = "onboarding"
    NAVIGATION = "navigation"
    ACCESSIBILITY = "accessibility"


@dataclass
class ContentFinding:
    """A UX content issue or recommendation"""
    finding_id: str
    title: str
    severity: Severity
    category: ContentCategory
    current_text: str
    recommended_text: str
    rationale: str
    voice_tone_issue: bool = False
    accessibility_issue: bool = False
    localization_issue: bool = False


@dataclass
class VoiceToneGuideline:
    """Voice and tone specification"""
    attribute: str
    description: str
    do_examples: List[str] = field(default_factory=list)
    dont_examples: List[str] = field(default_factory=list)


class EnhancedUXContentAssistant:
    """Enhanced UX Content Writer with comprehensive microcopy guidance"""

    def __init__(self):
        self.name = "Enhanced UX Content Writer"
        self.version = "2.0.0"
        self.guidelines = ["NNG", "Material Design", "Apple HIG", "Microsoft"]

    # =========================================================================
    # BUTTON AND ACTION TEXT PATTERNS
    # =========================================================================

    @staticmethod
    def button_patterns() -> Dict[str, Any]:
        """Comprehensive button and action text patterns"""
        return {
            "primary_actions": {
                "description": "Main actions users take",
                "patterns": {
                    "creation": {
                        "preferred": ["Create", "Add", "New"],
                        "avoid": ["Submit", "Make", "Generate"],
                        "examples": {
                            "good": [
                                "Create account",
                                "Add to cart",
                                "New project",
                            ],
                            "bad": [
                                "Submit",  # Too vague
                                "Make it",  # Informal
                                "Generate new",  # Redundant
                            ],
                        },
                    },
                    "submission": {
                        "preferred": ["Save", "Send", "Publish"],
                        "context_specific": {
                            "forms": "Save",
                            "messages": "Send",
                            "content": "Publish",
                            "payments": "Pay $XX.XX",  # Show amount
                        },
                        "examples": {
                            "good": [
                                "Save changes",
                                "Send message",
                                "Publish post",
                                "Pay $29.99",
                            ],
                            "bad": [
                                "Submit",  # Generic
                                "Done",  # Ambiguous
                                "OK",  # Doesn't describe action
                            ],
                        },
                    },
                    "continuation": {
                        "preferred": ["Continue", "Next", "Proceed"],
                        "examples": {
                            "good": [
                                "Continue to checkout",
                                "Next: Review order",
                                "Proceed to payment",
                            ],
                            "bad": [
                                "Go",  # Too vague
                                "Forward",  # Confusing
                                "Continue...",  # Ellipsis unnecessary
                            ],
                        },
                    },
                },
            },
            "secondary_actions": {
                "description": "Alternative or supporting actions",
                "patterns": {
                    "cancellation": {
                        "preferred": ["Cancel", "Go back", "Not now"],
                        "context": "Use 'Cancel' for dialogs, 'Go back' for navigation",
                        "examples": {
                            "good": ["Cancel", "Go back", "Not now", "Skip"],
                            "bad": [
                                "Abort",  # Too technical
                                "Nevermind",  # Too casual
                                "X",  # Not accessible
                            ],
                        },
                    },
                    "dismissal": {
                        "preferred": ["Dismiss", "Close", "Got it"],
                        "examples": {
                            "good": [
                                "Dismiss",
                                "Close",
                                "Got it",
                                "Okay, thanks",
                            ],
                            "bad": [
                                "Whatever",  # Dismissive
                                "Fine",  # Passive aggressive
                            ],
                        },
                    },
                },
            },
            "destructive_actions": {
                "description": "Actions that remove or permanently change data",
                "patterns": {
                    "deletion": {
                        "preferred": ["Delete", "Remove"],
                        "format": "Delete [item]",
                        "examples": {
                            "good": [
                                "Delete account",
                                "Remove from cart",
                                "Delete message",
                            ],
                            "bad": [
                                "Destroy",  # Too dramatic
                                "Eliminate",  # Too formal
                                "Trash",  # Too casual for permanent actions
                            ],
                        },
                    },
                    "require_confirmation": [
                        "Delete account",
                        "Remove all data",
                        "Cancel subscription",
                        "Leave organization",
                    ],
                },
            },
            "button_formatting": {
                "capitalization": {
                    "title_case": "iOS, some enterprise apps",
                    "sentence_case": "Android, Google, most web apps (recommended)",
                    "example_title": "Create New Project",
                    "example_sentence": "Create new project",
                },
                "length": {
                    "ideal": "1-3 words",
                    "maximum": "4-5 words",
                    "examples": {
                        "good": ["Save", "Send message", "Add to cart"],
                        "too_long": ["Click here to save your changes"],
                    },
                },
                "verb_first": {
                    "rule": "Start with a verb for action buttons",
                    "examples": {
                        "good": ["Save draft", "Export data", "Invite team"],
                        "bad": ["Draft save", "Data export", "Team invitation"],
                    },
                },
            },
        }

    # =========================================================================
    # ERROR MESSAGE FRAMEWORK
    # =========================================================================

    @staticmethod
    def error_message_framework() -> Dict[str, Any]:
        """Comprehensive error message patterns"""
        return {
            "structure": {
                "description": "Error message anatomy",
                "components": [
                    "What happened (brief, clear)",
                    "Why it happened (if helpful)",
                    "How to fix it (actionable)",
                ],
                "example": {
                    "what": "Couldn't save your changes.",
                    "why": "You're currently offline.",
                    "how": "Check your connection and try again.",
                    "full": "Couldn't save your changes. You're currently offline. Check your connection and try again.",
                },
            },
            "validation_errors": {
                "inline_format": {
                    "description": "Show next to the field",
                    "patterns": {
                        "required": {
                            "good": "Email is required",
                            "bad": "This field is required",  # Not specific
                        },
                        "format": {
                            "good": "Enter a valid email address (e.g., name@example.com)",
                            "bad": "Invalid email",  # Doesn't help fix
                        },
                        "length": {
                            "good": "Password must be at least 8 characters",
                            "bad": "Too short",  # Not specific
                        },
                        "range": {
                            "good": "Enter a number between 1 and 100",
                            "bad": "Invalid number",  # Doesn't give range
                        },
                        "unique": {
                            "good": "This email is already registered. Sign in instead?",
                            "bad": "Email already exists",  # No next step
                        },
                    },
                },
                "real_time_validation": {
                    "timing": "Validate on blur, not on every keystroke",
                    "positive_feedback": "Show checkmarks for valid fields",
                    "example_flow": [
                        "User types in email field",
                        "User tabs to next field",
                        "Validation runs",
                        "If invalid: show inline error",
                        "If valid: show green checkmark (optional)",
                    ],
                },
            },
            "system_errors": {
                "categories": {
                    "network": {
                        "offline": {
                            "message": "You're offline. Check your connection and try again.",
                            "action": "Try again",
                        },
                        "timeout": {
                            "message": "This is taking longer than expected. Please wait or try again.",
                            "action": "Wait | Try again",
                        },
                        "server_error": {
                            "message": "Something went wrong on our end. Please try again in a few minutes.",
                            "action": "Try again",
                        },
                    },
                    "permissions": {
                        "unauthorized": {
                            "message": "You don't have permission to do this. Contact your admin for access.",
                            "action": "Contact admin",
                        },
                        "session_expired": {
                            "message": "Your session has expired. Please sign in again.",
                            "action": "Sign in",
                        },
                    },
                    "data": {
                        "not_found": {
                            "message": "We couldn't find what you're looking for. It may have been moved or deleted.",
                            "action": "Go back",
                        },
                        "conflict": {
                            "message": "This item was updated by someone else. Refresh to see the latest version.",
                            "action": "Refresh",
                        },
                    },
                },
            },
            "error_tone": {
                "principles": [
                    "Be helpful, not blaming",
                    "Be specific about what went wrong",
                    "Provide a clear next step",
                    "Avoid technical jargon",
                    "Don't use negative words excessively",
                ],
                "examples": {
                    "good": [
                        "Couldn't connect. Check your internet and try again.",
                        "This file is too large. Choose a file under 10MB.",
                        "Something went wrong. Please try again.",
                    ],
                    "bad": [
                        "Error 500: Internal Server Error",
                        "FAILED: Connection refused",
                        "You made a mistake in the form",
                        "Invalid input detected",
                    ],
                },
            },
            "code_examples": {
                "error_component": '''
// React Error Message Component
interface ErrorMessageProps {
  type: 'inline' | 'toast' | 'page';
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  type,
  message,
  action
}) => {
  return (
    <div
      role="alert"
      aria-live="polite"
      className={`error-message error-message--${type}`}
    >
      <span className="error-message__icon" aria-hidden="true">
        ⚠️
      </span>
      <span className="error-message__text">{message}</span>
      {action && (
        <button
          onClick={action.onClick}
          className="error-message__action"
        >
          {action.label}
        </button>
      )}
    </div>
  );
};

// Usage
<ErrorMessage
  type="inline"
  message="Enter a valid email address"
/>

<ErrorMessage
  type="toast"
  message="Couldn't save changes. You're offline."
  action={{
    label: "Try again",
    onClick: handleRetry
  }}
/>
''',
                "validation_messages": '''
// Validation Message Library
const validationMessages = {
  required: (field: string) => `${field} is required`,

  email: () => "Enter a valid email address (e.g., name@example.com)",

  minLength: (field: string, min: number) =>
    `${field} must be at least ${min} characters`,

  maxLength: (field: string, max: number) =>
    `${field} must be ${max} characters or less`,

  pattern: {
    phone: () => "Enter a valid phone number (e.g., 555-123-4567)",
    url: () => "Enter a valid URL (e.g., https://example.com)",
    password: () => "Password must include a number and a special character",
  },

  range: (field: string, min: number, max: number) =>
    `${field} must be between ${min} and ${max}`,

  unique: (field: string) =>
    `This ${field.toLowerCase()} is already taken`,

  match: (field1: string, field2: string) =>
    `${field1} must match ${field2}`,
};

// Usage with form library
const schema = yup.object({
  email: yup
    .string()
    .required(validationMessages.required("Email"))
    .email(validationMessages.email()),
  password: yup
    .string()
    .required(validationMessages.required("Password"))
    .min(8, validationMessages.minLength("Password", 8)),
});
''',
            },
        }

    # =========================================================================
    # EMPTY STATES
    # =========================================================================

    @staticmethod
    def empty_state_patterns() -> Dict[str, Any]:
        """Patterns for empty states and zero-data scenarios"""
        return {
            "structure": {
                "components": [
                    "Illustration or icon (optional)",
                    "Headline (what's empty)",
                    "Description (why it matters)",
                    "Action (how to fill it)",
                ],
                "example": {
                    "headline": "No projects yet",
                    "description": "Projects help you organize your work. Create your first one to get started.",
                    "action": "Create project",
                },
            },
            "types": {
                "first_use": {
                    "description": "User hasn't created anything yet",
                    "tone": "Welcoming, encouraging",
                    "examples": {
                        "projects": {
                            "headline": "No projects yet",
                            "description": "Create a project to start organizing your work.",
                            "action": "Create your first project",
                        },
                        "messages": {
                            "headline": "Your inbox is empty",
                            "description": "Messages from your team will appear here.",
                            "action": "Invite teammates",
                        },
                        "files": {
                            "headline": "No files uploaded",
                            "description": "Drag and drop files here or click to upload.",
                            "action": "Upload files",
                        },
                    },
                },
                "no_results": {
                    "description": "Search or filter returned nothing",
                    "tone": "Helpful, suggesting alternatives",
                    "examples": {
                        "search": {
                            "headline": "No results for \"{query}\"",
                            "description": "Try different keywords or check your spelling.",
                            "action": "Clear search",
                        },
                        "filter": {
                            "headline": "No matching items",
                            "description": "Try adjusting your filters to see more results.",
                            "action": "Clear filters",
                        },
                    },
                },
                "cleared": {
                    "description": "User intentionally emptied the content",
                    "tone": "Positive, accomplished",
                    "examples": {
                        "tasks": {
                            "headline": "All done!",
                            "description": "You've completed all your tasks. Time for a break?",
                            "action": "Add new task",
                        },
                        "notifications": {
                            "headline": "All caught up",
                            "description": "You've seen all your notifications.",
                            "action": None,
                        },
                    },
                },
                "error": {
                    "description": "Content couldn't be loaded",
                    "tone": "Apologetic, actionable",
                    "examples": {
                        "load_failure": {
                            "headline": "Couldn't load content",
                            "description": "Something went wrong. Please try again.",
                            "action": "Retry",
                        },
                        "permission": {
                            "headline": "You don't have access",
                            "description": "Ask the owner to share this with you.",
                            "action": "Request access",
                        },
                    },
                },
            },
            "code_example": '''
// React Empty State Component
interface EmptyStateProps {
  type: 'first_use' | 'no_results' | 'cleared' | 'error';
  icon?: React.ReactNode;
  headline: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary';
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
}

const EmptyState: React.FC<EmptyStateProps> = ({
  type,
  icon,
  headline,
  description,
  action,
  secondaryAction,
}) => {
  return (
    <div className={`empty-state empty-state--${type}`}>
      {icon && (
        <div className="empty-state__icon" aria-hidden="true">
          {icon}
        </div>
      )}

      <h2 className="empty-state__headline">{headline}</h2>

      {description && (
        <p className="empty-state__description">{description}</p>
      )}

      {action && (
        <button
          onClick={action.onClick}
          className={`button button--${action.variant || 'primary'}`}
        >
          {action.label}
        </button>
      )}

      {secondaryAction && (
        <button
          onClick={secondaryAction.onClick}
          className="button button--link"
        >
          {secondaryAction.label}
        </button>
      )}
    </div>
  );
};

// Usage Examples
<EmptyState
  type="first_use"
  icon={<ProjectIcon />}
  headline="No projects yet"
  description="Projects help you organize your work."
  action={{
    label: "Create your first project",
    onClick: handleCreateProject,
  }}
/>

<EmptyState
  type="no_results"
  icon={<SearchIcon />}
  headline={`No results for "${query}"`}
  description="Try different keywords or check your spelling."
  action={{
    label: "Clear search",
    onClick: handleClearSearch,
    variant: "secondary",
  }}
/>
''',
        }

    # =========================================================================
    # LOADING AND PROGRESS
    # =========================================================================

    @staticmethod
    def loading_patterns() -> Dict[str, Any]:
        """Loading states and progress indicators"""
        return {
            "loading_types": {
                "indeterminate": {
                    "use_when": "Duration unknown",
                    "patterns": [
                        "Loading...",
                        "Please wait...",
                        "Getting your data...",
                    ],
                    "avoid": [
                        "Loading, please wait...",  # Redundant
                        "Just a moment...",  # Vague promise
                    ],
                },
                "determinate": {
                    "use_when": "Progress can be measured",
                    "patterns": [
                        "Uploading... 45%",
                        "3 of 10 items processed",
                        "Downloading: 2.5 MB of 10 MB",
                    ],
                },
                "skeleton": {
                    "use_when": "Layout is known",
                    "note": "No text needed - the shape communicates loading",
                },
            },
            "contextual_loading": {
                "by_action": {
                    "save": ["Saving...", "Saved!", "Couldn't save"],
                    "send": ["Sending...", "Sent!", "Couldn't send"],
                    "delete": ["Deleting...", "Deleted", "Couldn't delete"],
                    "upload": ["Uploading...", "Uploaded!", "Upload failed"],
                    "search": ["Searching...", None, "Search failed"],
                },
                "by_duration": {
                    "instant": "No loading state needed (< 100ms)",
                    "short": "Spinner only (100ms - 1s)",
                    "medium": "Spinner + text (1s - 10s)",
                    "long": "Progress bar + details (> 10s)",
                },
            },
            "progress_messages": {
                "file_operations": {
                    "upload_single": "Uploading {filename}...",
                    "upload_multiple": "Uploading {count} files...",
                    "download": "Downloading {filename}...",
                    "processing": "Processing {filename}...",
                },
                "data_operations": {
                    "sync": "Syncing your data...",
                    "import": "Importing {count} records...",
                    "export": "Preparing your export...",
                    "backup": "Backing up your data...",
                },
                "multi_step": {
                    "pattern": "Step {current} of {total}: {action}",
                    "examples": [
                        "Step 1 of 3: Validating data",
                        "Step 2 of 3: Processing records",
                        "Step 3 of 3: Generating report",
                    ],
                },
            },
            "code_example": '''
// React Loading State Hook
import { useState, useCallback } from 'react';

type LoadingState = 'idle' | 'loading' | 'success' | 'error';

interface UseLoadingStateReturn<T> {
  state: LoadingState;
  data: T | null;
  error: string | null;
  execute: (promise: Promise<T>) => Promise<void>;
  reset: () => void;
}

function useLoadingState<T>(): UseLoadingStateReturn<T> {
  const [state, setState] = useState<LoadingState>('idle');
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (promise: Promise<T>) => {
    setState('loading');
    setError(null);

    try {
      const result = await promise;
      setData(result);
      setState('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setState('error');
    }
  }, []);

  const reset = useCallback(() => {
    setState('idle');
    setData(null);
    setError(null);
  }, []);

  return { state, data, error, execute, reset };
}

// Loading Button Component
interface LoadingButtonProps {
  onClick: () => Promise<void>;
  children: React.ReactNode;
  loadingText?: string;
  successText?: string;
  errorText?: string;
}

const loadingMessages = {
  save: { loading: 'Saving...', success: 'Saved!', error: "Couldn't save" },
  send: { loading: 'Sending...', success: 'Sent!', error: "Couldn't send" },
  delete: { loading: 'Deleting...', success: 'Deleted', error: "Couldn't delete" },
};

const LoadingButton: React.FC<LoadingButtonProps> = ({
  onClick,
  children,
  loadingText = 'Loading...',
  successText = 'Done!',
  errorText = 'Failed',
}) => {
  const { state, execute } = useLoadingState<void>();

  const getText = () => {
    switch (state) {
      case 'loading': return loadingText;
      case 'success': return successText;
      case 'error': return errorText;
      default: return children;
    }
  };

  return (
    <button
      onClick={() => execute(onClick())}
      disabled={state === 'loading'}
      aria-busy={state === 'loading'}
      className={`button button--${state}`}
    >
      {state === 'loading' && <Spinner aria-hidden="true" />}
      <span>{getText()}</span>
    </button>
  );
};
''',
        }

    # =========================================================================
    # CONFIRMATION DIALOGS
    # =========================================================================

    @staticmethod
    def confirmation_patterns() -> Dict[str, Any]:
        """Confirmation dialog patterns for destructive actions"""
        return {
            "when_to_confirm": {
                "always_confirm": [
                    "Permanent deletion",
                    "Account closure",
                    "Data export (sensitive)",
                    "Subscription cancellation",
                    "Permission changes",
                ],
                "consider_confirming": [
                    "Sending to many recipients",
                    "Large batch operations",
                    "Publishing content",
                    "Irreversible state changes",
                ],
                "dont_confirm": [
                    "Save operations",
                    "Navigation",
                    "Easily reversible actions",
                    "Toggle settings (use undo instead)",
                ],
            },
            "dialog_structure": {
                "components": {
                    "title": "What will happen",
                    "description": "Consequences and any data loss",
                    "confirm_button": "Specific action verb",
                    "cancel_button": "Cancel or Go back",
                },
                "examples": {
                    "delete_item": {
                        "title": "Delete this project?",
                        "description": "This will permanently delete \"My Project\" and all its contents. This action cannot be undone.",
                        "confirm": "Delete project",
                        "cancel": "Cancel",
                    },
                    "cancel_subscription": {
                        "title": "Cancel your subscription?",
                        "description": "You'll lose access to premium features on {date}. You can resubscribe anytime.",
                        "confirm": "Cancel subscription",
                        "cancel": "Keep subscription",
                    },
                    "close_account": {
                        "title": "Close your account?",
                        "description": "This will permanently delete your account and all your data. This cannot be undone.",
                        "confirm": "Yes, close my account",
                        "cancel": "Keep my account",
                    },
                    "unsaved_changes": {
                        "title": "Unsaved changes",
                        "description": "You have unsaved changes. Do you want to save them before leaving?",
                        "confirm": "Save and leave",
                        "secondary": "Leave without saving",
                        "cancel": "Stay on page",
                    },
                },
            },
            "button_patterns": {
                "destructive_confirm": {
                    "rule": "Make the destructive action explicit",
                    "good": ["Delete project", "Remove user", "Cancel subscription"],
                    "bad": ["Yes", "OK", "Confirm", "Delete"],  # Too vague
                },
                "non_destructive_cancel": {
                    "rule": "Cancel should feel safe",
                    "good": ["Cancel", "Go back", "Keep editing", "Not now"],
                    "bad": ["No", "Abort", "Dismiss"],
                },
            },
            "high_stakes_confirmation": {
                "description": "For very destructive actions, require explicit confirmation",
                "patterns": {
                    "type_to_confirm": {
                        "instruction": "Type DELETE to confirm",
                        "use_for": "Account deletion, organization deletion",
                    },
                    "checkbox_confirm": {
                        "label": "I understand this action cannot be undone",
                        "use_for": "Data deletion, subscription cancellation",
                    },
                    "waiting_period": {
                        "message": "Your account will be deleted in 14 days. You can cancel this during that time.",
                        "use_for": "Account deletion with grace period",
                    },
                },
            },
            "code_example": '''
// React Confirmation Dialog
interface ConfirmDialogProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  title: string;
  description: string;
  confirmLabel: string;
  cancelLabel?: string;
  variant?: 'default' | 'destructive';
  requiresTyping?: string;  // Text user must type to confirm
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  onConfirm,
  onCancel,
  title,
  description,
  confirmLabel,
  cancelLabel = 'Cancel',
  variant = 'default',
  requiresTyping,
}) => {
  const [typedText, setTypedText] = useState('');
  const canConfirm = !requiresTyping || typedText === requiresTyping;

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onCancel}
      aria-labelledby="confirm-title"
      aria-describedby="confirm-description"
    >
      <h2 id="confirm-title">{title}</h2>

      <p id="confirm-description">{description}</p>

      {requiresTyping && (
        <div className="confirm-typing">
          <label htmlFor="confirm-input">
            Type <strong>{requiresTyping}</strong> to confirm
          </label>
          <input
            id="confirm-input"
            type="text"
            value={typedText}
            onChange={(e) => setTypedText(e.target.value)}
            autoComplete="off"
          />
        </div>
      )}

      <div className="dialog-actions">
        <button
          onClick={onCancel}
          className="button button--secondary"
        >
          {cancelLabel}
        </button>
        <button
          onClick={onConfirm}
          disabled={!canConfirm}
          className={`button button--${variant}`}
        >
          {confirmLabel}
        </button>
      </div>
    </Dialog>
  );
};

// Usage
<ConfirmDialog
  isOpen={showDeleteDialog}
  title="Delete this project?"
  description="This will permanently delete 'My Project' and all its contents."
  confirmLabel="Delete project"
  cancelLabel="Cancel"
  variant="destructive"
  onConfirm={handleDelete}
  onCancel={() => setShowDeleteDialog(false)}
/>

// High-stakes deletion
<ConfirmDialog
  isOpen={showAccountDeleteDialog}
  title="Delete your account?"
  description="This will permanently delete your account and all data."
  confirmLabel="Delete my account"
  cancelLabel="Keep my account"
  variant="destructive"
  requiresTyping="DELETE"
  onConfirm={handleDeleteAccount}
  onCancel={() => setShowAccountDeleteDialog(false)}
/>
''',
        }

    # =========================================================================
    # FORM LABELS AND HELP TEXT
    # =========================================================================

    @staticmethod
    def form_content_patterns() -> Dict[str, Any]:
        """Form labels, placeholders, and help text"""
        return {
            "labels": {
                "principles": [
                    "Use nouns, not verbs (Email, not Enter email)",
                    "Be specific (Work email, not just Email)",
                    "Keep short (2-3 words max)",
                    "Mark optional fields, not required (most fields are required)",
                ],
                "examples": {
                    "good": [
                        "Email address",
                        "Password",
                        "Full name",
                        "Company (optional)",
                        "Phone number",
                    ],
                    "bad": [
                        "Enter your email",  # Verb form
                        "Email*",  # Star for required
                        "What is your email address?",  # Too long
                        "E-mail",  # Inconsistent hyphen
                    ],
                },
            },
            "placeholders": {
                "purpose": "Show format, not repeat label",
                "principles": [
                    "Don't repeat the label",
                    "Show example format",
                    "Don't use as label replacement",
                ],
                "examples": {
                    "good": {
                        "email": "name@example.com",
                        "phone": "555-123-4567",
                        "url": "https://example.com",
                        "date": "MM/DD/YYYY",
                        "search": "Search projects...",
                    },
                    "bad": {
                        "email": "Enter your email",  # Repeats label
                        "phone": "Phone number",  # Is the label
                        "name": "Required",  # Not helpful
                    },
                },
            },
            "help_text": {
                "purpose": "Provide additional context or requirements",
                "placement": "Below the input field",
                "examples": {
                    "password": "Must be at least 8 characters with a number and symbol",
                    "username": "Only letters, numbers, and underscores. 3-20 characters.",
                    "bio": "Brief description for your profile. 160 characters max.",
                    "file": "PNG, JPG, or GIF. Max 5MB.",
                },
            },
            "character_counts": {
                "when_to_show": "When there's a character limit",
                "format": {
                    "remaining": "42 characters remaining",
                    "used": "118/160",
                    "over_limit": "20 characters over limit",
                },
            },
            "code_example": '''
// Form Field Component with Help Text
interface FormFieldProps {
  label: string;
  name: string;
  type?: string;
  placeholder?: string;
  helpText?: string;
  error?: string;
  optional?: boolean;
  maxLength?: number;
  value: string;
  onChange: (value: string) => void;
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  type = 'text',
  placeholder,
  helpText,
  error,
  optional = false,
  maxLength,
  value,
  onChange,
}) => {
  const helpId = `${name}-help`;
  const errorId = `${name}-error`;
  const describedBy = [
    helpText && helpId,
    error && errorId,
  ].filter(Boolean).join(' ');

  return (
    <div className={`form-field ${error ? 'form-field--error' : ''}`}>
      <label htmlFor={name} className="form-field__label">
        {label}
        {optional && <span className="form-field__optional"> (optional)</span>}
      </label>

      <input
        id={name}
        name={name}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        maxLength={maxLength}
        aria-describedby={describedBy || undefined}
        aria-invalid={error ? 'true' : undefined}
        className="form-field__input"
      />

      {helpText && !error && (
        <p id={helpId} className="form-field__help">
          {helpText}
        </p>
      )}

      {error && (
        <p id={errorId} className="form-field__error" role="alert">
          {error}
        </p>
      )}

      {maxLength && (
        <p className="form-field__count" aria-live="polite">
          {value.length}/{maxLength}
        </p>
      )}
    </div>
  );
};

// Usage
<FormField
  label="Bio"
  name="bio"
  placeholder="Tell us about yourself"
  helpText="Brief description for your profile"
  maxLength={160}
  value={bio}
  onChange={setBio}
  optional
/>

<FormField
  label="Password"
  name="password"
  type="password"
  helpText="At least 8 characters with a number and symbol"
  value={password}
  onChange={setPassword}
  error={passwordError}
/>
''',
        }

    # =========================================================================
    # NOTIFICATIONS AND TOASTS
    # =========================================================================

    @staticmethod
    def notification_patterns() -> Dict[str, Any]:
        """Notification and toast message patterns"""
        return {
            "types": {
                "success": {
                    "purpose": "Confirm completed action",
                    "tone": "Brief, positive",
                    "examples": [
                        "Saved",
                        "Message sent",
                        "Profile updated",
                        "File uploaded",
                        "Changes published",
                    ],
                    "avoid": [
                        "Successfully saved!",  # Redundant
                        "Your changes have been successfully saved to the database",  # Too long
                    ],
                },
                "error": {
                    "purpose": "Alert to failed action",
                    "tone": "Helpful, actionable",
                    "examples": [
                        "Couldn't save. Try again.",
                        "Upload failed. File too large.",
                        "Connection lost. Retrying...",
                    ],
                },
                "warning": {
                    "purpose": "Alert to potential issue",
                    "tone": "Cautionary but not alarming",
                    "examples": [
                        "Unsaved changes",
                        "Session expires in 5 minutes",
                        "Storage almost full",
                    ],
                },
                "info": {
                    "purpose": "Provide helpful information",
                    "tone": "Neutral, informative",
                    "examples": [
                        "New features available",
                        "3 tasks due today",
                        "Update available",
                    ],
                },
            },
            "duration": {
                "auto_dismiss": {
                    "success": "3-5 seconds",
                    "info": "5-7 seconds",
                    "warning": "Until dismissed or 10 seconds",
                    "error": "Until dismissed (for actionable errors)",
                },
            },
            "action_feedback": {
                "pattern": "{Action} {result}",
                "examples": {
                    "copy": {
                        "start": None,  # Too fast for feedback
                        "success": "Copied to clipboard",
                        "error": "Couldn't copy",
                    },
                    "save": {
                        "start": "Saving...",
                        "success": "Saved",
                        "error": "Couldn't save. Try again.",
                    },
                    "delete": {
                        "start": "Deleting...",
                        "success": "Deleted",
                        "error": "Couldn't delete",
                        "undo": "Item deleted. Undo",
                    },
                    "send": {
                        "start": "Sending...",
                        "success": "Sent",
                        "error": "Couldn't send. Try again.",
                    },
                },
            },
            "undo_pattern": {
                "format": "{Action completed}. {Undo link}",
                "examples": [
                    "Message archived. Undo",
                    "Email deleted. Undo",
                    "Task completed. Undo",
                ],
                "duration": "5-10 seconds to undo",
            },
            "code_example": '''
// Toast Notification System
type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastOptions {
  type: ToastType;
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  duration?: number;
  dismissible?: boolean;
}

const defaultDurations: Record<ToastType, number> = {
  success: 3000,
  info: 5000,
  warning: 7000,
  error: 0, // Don't auto-dismiss errors
};

// Toast Context and Hook
const ToastContext = createContext<{
  show: (options: ToastOptions) => void;
  dismiss: (id: string) => void;
} | null>(null);

function useToast() {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within ToastProvider');
  return context;
}

// Convenient toast methods
const toast = {
  success: (message: string) =>
    showToast({ type: 'success', message }),

  error: (message: string, action?: ToastOptions['action']) =>
    showToast({ type: 'error', message, action }),

  info: (message: string) =>
    showToast({ type: 'info', message }),

  warning: (message: string) =>
    showToast({ type: 'warning', message }),

  // With undo action
  withUndo: (message: string, onUndo: () => void) =>
    showToast({
      type: 'success',
      message,
      action: { label: 'Undo', onClick: onUndo },
      duration: 7000,
    }),
};

// Usage
const handleDelete = async (item: Item) => {
  const backup = { ...item };

  // Optimistic delete
  removeItem(item.id);

  toast.withUndo(`${item.name} deleted`, () => {
    // Undo: restore the item
    restoreItem(backup);
  });

  // Actually delete after undo window
  setTimeout(() => {
    api.deleteItem(item.id);
  }, 7000);
};

// Action feedback
const handleSave = async () => {
  toast.info('Saving...');

  try {
    await api.save(data);
    toast.success('Saved');
  } catch (error) {
    toast.error("Couldn't save. Try again.", {
      label: 'Retry',
      onClick: handleSave,
    });
  }
};
''',
        }

    # =========================================================================
    # ONBOARDING AND TUTORIALS
    # =========================================================================

    @staticmethod
    def onboarding_patterns() -> Dict[str, Any]:
        """Onboarding flow and tutorial content"""
        return {
            "welcome_screens": {
                "structure": {
                    "headline": "Clear value proposition",
                    "description": "What the user can do",
                    "action": "Get started action",
                },
                "examples": {
                    "simple": {
                        "headline": "Welcome to {App}",
                        "description": "The easiest way to {core value}",
                        "action": "Get started",
                    },
                    "feature_highlight": {
                        "screens": [
                            {
                                "headline": "Organize your projects",
                                "description": "Keep all your work in one place",
                            },
                            {
                                "headline": "Collaborate with your team",
                                "description": "Share and work together in real-time",
                            },
                            {
                                "headline": "Track your progress",
                                "description": "See what's done and what's next",
                            },
                        ],
                        "navigation": "Skip | Next | Done",
                    },
                },
            },
            "tooltips": {
                "structure": {
                    "title": "Feature name (optional)",
                    "description": "What it does, why it matters",
                    "action": "Try it | Got it | Next",
                },
                "examples": [
                    {
                        "title": "Quick actions",
                        "description": "Press / to open the command menu",
                        "action": "Got it",
                    },
                    {
                        "title": None,
                        "description": "Drag tasks to reorder them",
                        "action": "Next",
                    },
                ],
                "best_practices": [
                    "Keep under 2 sentences",
                    "Focus on one feature at a time",
                    "Allow skipping entire tour",
                    "Show progress (1 of 5)",
                ],
            },
            "coach_marks": {
                "purpose": "Point to specific UI elements",
                "examples": {
                    "button": {
                        "point_to": "Create button",
                        "text": "Start here to create your first project",
                    },
                    "feature": {
                        "point_to": "Sidebar",
                        "text": "Find all your projects and teams here",
                    },
                },
            },
            "progressive_disclosure": {
                "principle": "Reveal features as users need them",
                "examples": {
                    "first_project": {
                        "trigger": "User creates first project",
                        "reveal": "Show collaboration features",
                    },
                    "advanced_features": {
                        "trigger": "User completes 5 tasks",
                        "reveal": "Introduce keyboard shortcuts",
                    },
                },
            },
            "code_example": '''
// Onboarding Tour Component
interface TourStep {
  target: string;  // CSS selector
  title?: string;
  content: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  action?: {
    label: string;
    onClick?: () => void;
  };
}

const onboardingSteps: TourStep[] = [
  {
    target: '[data-tour="create-button"]',
    title: 'Create your first project',
    content: 'Click here to get started',
    placement: 'bottom',
    action: { label: 'Next' },
  },
  {
    target: '[data-tour="sidebar"]',
    content: 'Find all your projects here',
    placement: 'right',
    action: { label: 'Next' },
  },
  {
    target: '[data-tour="search"]',
    title: 'Quick search',
    content: 'Press ⌘K to search anything',
    placement: 'bottom',
    action: { label: 'Got it' },
  },
];

// Tour Hook
function useOnboardingTour(steps: TourStep[]) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isActive, setIsActive] = useState(false);

  const start = useCallback(() => {
    setCurrentStep(0);
    setIsActive(true);
  }, []);

  const next = useCallback(() => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      setIsActive(false);
      markOnboardingComplete();
    }
  }, [currentStep, steps.length]);

  const skip = useCallback(() => {
    setIsActive(false);
    markOnboardingComplete();
  }, []);

  return {
    isActive,
    currentStep,
    step: steps[currentStep],
    totalSteps: steps.length,
    start,
    next,
    skip,
  };
}

// Welcome Screen Component
interface WelcomeScreenProps {
  headline: string;
  description: string;
  action: {
    label: string;
    onClick: () => void;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  headline,
  description,
  action,
  secondaryAction,
}) => (
  <div className="welcome-screen">
    <h1 className="welcome-screen__headline">{headline}</h1>
    <p className="welcome-screen__description">{description}</p>

    <div className="welcome-screen__actions">
      <button
        onClick={action.onClick}
        className="button button--primary"
      >
        {action.label}
      </button>

      {secondaryAction && (
        <button
          onClick={secondaryAction.onClick}
          className="button button--link"
        >
          {secondaryAction.label}
        </button>
      )}
    </div>
  </div>
);
''',
        }

    # =========================================================================
    # VOICE AND TONE GUIDELINES
    # =========================================================================

    @staticmethod
    def voice_and_tone() -> Dict[str, Any]:
        """Voice and tone guidelines for consistent UX writing"""
        return {
            "voice_attributes": {
                "description": "Voice is consistent; tone adapts to context",
                "attributes": [
                    {
                        "attribute": "Clear",
                        "description": "Easy to understand, no jargon",
                        "do": [
                            "Your changes are saved",
                            "Something went wrong",
                            "Sign in to continue",
                        ],
                        "dont": [
                            "Persistence operation completed",
                            "An unexpected error occurred",
                            "Authentication required",
                        ],
                    },
                    {
                        "attribute": "Concise",
                        "description": "Say more with less",
                        "do": [
                            "Delete project?",
                            "Saved",
                            "2 items selected",
                        ],
                        "dont": [
                            "Are you sure you want to delete?",
                            "Successfully saved!",
                            "You have selected 2 items",
                        ],
                    },
                    {
                        "attribute": "Helpful",
                        "description": "Guide users to success",
                        "do": [
                            "Enter a valid email (e.g., name@example.com)",
                            "Couldn't connect. Check your internet.",
                            "No results. Try different keywords.",
                        ],
                        "dont": [
                            "Invalid email",
                            "Connection failed",
                            "No results found",
                        ],
                    },
                    {
                        "attribute": "Human",
                        "description": "Natural, not robotic",
                        "do": [
                            "Hmm, we couldn't find that",
                            "All done!",
                            "Welcome back",
                        ],
                        "dont": [
                            "Error: Resource not found",
                            "Operation complete",
                            "User authenticated",
                        ],
                    },
                ],
            },
            "tone_by_context": {
                "success": {
                    "tone": "Positive, brief",
                    "examples": ["Done!", "Saved", "Sent"],
                },
                "error": {
                    "tone": "Helpful, not blaming",
                    "examples": [
                        "Something went wrong. Try again.",
                        "Couldn't save. You're offline.",
                    ],
                },
                "empty": {
                    "tone": "Encouraging, actionable",
                    "examples": [
                        "No projects yet. Create one to get started.",
                    ],
                },
                "warning": {
                    "tone": "Clear, not alarming",
                    "examples": [
                        "This action can't be undone",
                        "Your session expires soon",
                    ],
                },
                "onboarding": {
                    "tone": "Welcoming, guiding",
                    "examples": [
                        "Let's get you set up",
                        "Here's how it works",
                    ],
                },
            },
            "writing_principles": {
                "lead_with_action": {
                    "description": "Put the most important info first",
                    "good": "Save your changes before leaving?",
                    "bad": "Before leaving, would you like to save?",
                },
                "use_active_voice": {
                    "description": "Subject performs the action",
                    "good": "We couldn't find that page",
                    "bad": "That page could not be found",
                },
                "avoid_double_negatives": {
                    "good": "Show completed tasks",
                    "bad": "Don't hide completed tasks",
                },
                "be_specific": {
                    "good": "Delete 3 files?",
                    "bad": "Delete selected items?",
                },
            },
        }

    # =========================================================================
    # INCLUSIVE LANGUAGE
    # =========================================================================

    @staticmethod
    def inclusive_language() -> Dict[str, Any]:
        """Inclusive language guidelines"""
        return {
            "principles": [
                "Use gender-neutral language",
                "Avoid ableist terms",
                "Be culturally aware",
                "Don't assume user characteristics",
            ],
            "gender_neutral": {
                "instead_of": {
                    "he/she": "they",
                    "his/her": "their",
                    "guys": "everyone, folks, team",
                    "mankind": "humanity, people",
                    "man-hours": "work hours, person-hours",
                    "chairman": "chair, chairperson",
                },
                "examples": {
                    "good": [
                        "Invite a teammate",
                        "Share with your team",
                        "When a user signs in, they see...",
                    ],
                    "bad": [
                        "Invite a guy from your team",
                        "Share with the guys",
                        "When a user signs in, he sees...",
                    ],
                },
            },
            "ableist_alternatives": {
                "instead_of": {
                    "crazy/insane": "unexpected, surprising, wild",
                    "blind to": "unaware of, ignoring",
                    "deaf to": "ignoring, dismissing",
                    "dumb": "silent, muted",
                    "lame": "unimpressive, weak",
                    "crippled": "broken, impaired, hindered",
                    "sanity check": "confidence check, validation",
                    "dummy": "placeholder, sample",
                },
            },
            "cultural_awareness": {
                "dates": {
                    "issue": "MM/DD/YYYY vs DD/MM/YYYY",
                    "solution": "Use month names or ISO format",
                    "examples": {
                        "good": ["Jan 15, 2024", "15 Jan 2024", "2024-01-15"],
                        "ambiguous": ["01/02/2024"],  # Jan 2 or Feb 1?
                    },
                },
                "names": {
                    "issue": "Not all names have first/last format",
                    "solution": "Use 'Full name' or 'Given name' + 'Family name'",
                },
                "currency": {
                    "issue": "$ means different currencies",
                    "solution": "Use currency codes: USD, EUR, GBP",
                },
                "colors": {
                    "issue": "Color meanings vary by culture",
                    "solution": "Don't rely on color alone to convey meaning",
                },
            },
            "avoid_assumptions": {
                "technical_ability": {
                    "avoid": "Simply click the button",
                    "better": "Click the Save button",
                },
                "familiarity": {
                    "avoid": "Use the usual method",
                    "better": "Sign in with your email",
                },
                "hardware": {
                    "avoid": "Right-click to open menu",
                    "better": "Open the menu (right-click or Ctrl+click)",
                },
            },
        }

    # =========================================================================
    # ACCESSIBILITY TEXT
    # =========================================================================

    @staticmethod
    def accessibility_text() -> Dict[str, Any]:
        """Accessibility-focused text patterns"""
        return {
            "alt_text": {
                "principles": [
                    "Describe the image's purpose, not appearance",
                    "Keep under 125 characters",
                    "Don't start with 'Image of...'",
                    "Use empty alt for decorative images",
                ],
                "patterns": {
                    "functional_images": {
                        "description": "Images that are buttons or links",
                        "examples": {
                            "good": [
                                'alt="Search"',  # Search icon button
                                'alt="Close dialog"',  # X button
                                'alt="Download PDF"',  # Download icon
                            ],
                            "bad": [
                                'alt="Magnifying glass icon"',
                                'alt="X"',
                                'alt="Arrow pointing down"',
                            ],
                        },
                    },
                    "informative_images": {
                        "description": "Images that convey information",
                        "examples": {
                            "good": [
                                'alt="Sales increased 25% in Q4"',  # Chart
                                'alt="Team photo: 12 members"',  # Photo
                            ],
                            "bad": [
                                'alt="Chart"',
                                'alt="Photo of people"',
                            ],
                        },
                    },
                    "decorative_images": {
                        "description": "Images that don't add information",
                        "examples": ['alt=""', 'role="presentation"'],
                    },
                },
            },
            "aria_labels": {
                "when_to_use": [
                    "Icon-only buttons",
                    "Complex interactive widgets",
                    "When visible text is insufficient",
                ],
                "patterns": {
                    "icon_buttons": {
                        "examples": [
                            '<button aria-label="Close">×</button>',
                            '<button aria-label="Menu"><MenuIcon /></button>',
                            '<button aria-label="Add to favorites"><HeartIcon /></button>',
                        ],
                    },
                    "status_updates": {
                        "examples": [
                            '<div aria-live="polite">3 results found</div>',
                            '<div aria-live="assertive">Error: Form invalid</div>',
                        ],
                    },
                    "dynamic_content": {
                        "examples": [
                            '<button aria-expanded="true" aria-controls="menu">Menu</button>',
                            '<div aria-busy="true">Loading...</div>',
                        ],
                    },
                },
            },
            "screen_reader_text": {
                "visually_hidden": {
                    "purpose": "Text only for screen readers",
                    "css": """
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
""",
                    "examples": [
                        '<span class="visually-hidden">External link</span>',
                        '<span class="visually-hidden">(opens in new tab)</span>',
                    ],
                },
            },
            "link_text": {
                "principles": [
                    "Describe the destination",
                    "Don't use 'click here' or 'read more'",
                    "Make sense out of context",
                ],
                "examples": {
                    "good": [
                        "View documentation",
                        "Download the report (PDF, 2MB)",
                        "Contact support",
                    ],
                    "bad": [
                        "Click here",
                        "Read more",
                        "Learn more",  # Without context
                    ],
                },
            },
            "code_example": '''
// Accessible Button Component
interface AccessibleButtonProps {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  showLabel?: boolean;
}

const AccessibleButton: React.FC<AccessibleButtonProps> = ({
  icon,
  label,
  onClick,
  showLabel = false,
}) => (
  <button
    onClick={onClick}
    aria-label={!showLabel ? label : undefined}
    className="button"
  >
    <span aria-hidden="true">{icon}</span>
    {showLabel ? (
      <span>{label}</span>
    ) : (
      <span className="visually-hidden">{label}</span>
    )}
  </button>
);

// Accessible Image Component
interface AccessibleImageProps {
  src: string;
  alt: string;
  isDecorative?: boolean;
}

const AccessibleImage: React.FC<AccessibleImageProps> = ({
  src,
  alt,
  isDecorative = false,
}) => (
  <img
    src={src}
    alt={isDecorative ? '' : alt}
    role={isDecorative ? 'presentation' : undefined}
  />
);

// Live Region for Status Updates
const StatusAnnouncer: React.FC<{
  message: string;
  priority: 'polite' | 'assertive';
}> = ({ message, priority }) => (
  <div
    role="status"
    aria-live={priority}
    aria-atomic="true"
    className="visually-hidden"
  >
    {message}
  </div>
);

// Usage
<StatusAnnouncer
  message="3 results found"
  priority="polite"
/>

<StatusAnnouncer
  message="Error: Please fix the form"
  priority="assertive"
/>
''',
        }

    # =========================================================================
    # LOCALIZATION CONSIDERATIONS
    # =========================================================================

    @staticmethod
    def localization_guidelines() -> Dict[str, Any]:
        """Localization and internationalization guidelines"""
        return {
            "text_expansion": {
                "description": "Translated text is often longer",
                "expansion_rates": {
                    "english_to_german": "30% longer",
                    "english_to_french": "20% longer",
                    "english_to_chinese": "May be shorter",
                },
                "design_tips": [
                    "Allow 30-40% extra space for text",
                    "Avoid fixed-width buttons",
                    "Test with pseudo-localization",
                ],
            },
            "string_formatting": {
                "use_placeholders": {
                    "good": "{count} items selected",
                    "bad": "You have selected " + count + " items",
                },
                "handle_plurals": {
                    "simple": {
                        "one": "1 item",
                        "other": "{count} items",
                    },
                    "complex_example": '''
// Using ICU MessageFormat
const messages = {
  'items.count': `{count, plural,
    =0 {No items}
    one {1 item}
    other {{count} items}
  }`
};
''',
                },
                "handle_gender": {
                    "issue": "Some languages have gendered nouns/adjectives",
                    "solution": "Use neutral phrasing when possible",
                },
            },
            "avoid_concatenation": {
                "description": "Word order varies by language",
                "examples": {
                    "bad": {
                        "code": '"Delete " + itemName + "?"',
                        "issue": "Word order may change in translation",
                    },
                    "good": {
                        "code": 'i18n.t("delete_confirm", { name: itemName })',
                        "template": 'Delete "{name}"?',
                    },
                },
            },
            "date_time_formats": {
                "use_locale_aware": {
                    "example": '''
// Use Intl.DateTimeFormat
const formatDate = (date: Date, locale: string) => {
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
};

formatDate(new Date(), 'en-US'); // "January 15, 2024"
formatDate(new Date(), 'de-DE'); // "15. Januar 2024"
formatDate(new Date(), 'ja-JP'); // "2024年1月15日"
''',
                },
                "relative_time": '''
// Use Intl.RelativeTimeFormat
const formatRelative = (date: Date, locale: string) => {
  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
  const days = Math.round((date.getTime() - Date.now()) / 86400000);
  return rtf.format(days, 'day');
};

formatRelative(yesterday, 'en-US'); // "yesterday"
formatRelative(yesterday, 'de-DE'); // "gestern"
''',
            },
            "numbers_currency": {
                "example": '''
// Use Intl.NumberFormat
const formatCurrency = (amount: number, currency: string, locale: string) => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(amount);
};

formatCurrency(1234.56, 'USD', 'en-US'); // "$1,234.56"
formatCurrency(1234.56, 'EUR', 'de-DE'); // "1.234,56 €"
formatCurrency(1234.56, 'JPY', 'ja-JP'); // "¥1,235"
''',
            },
            "rtl_support": {
                "languages": ["Arabic", "Hebrew", "Persian", "Urdu"],
                "considerations": [
                    "Mirror layout for RTL",
                    "Icons with direction may need flipping",
                    "Text alignment changes",
                ],
                "example": '''
// RTL-aware component
const DirectionalIcon: React.FC<{ name: string }> = ({ name }) => {
  const { direction } = useLocale();
  const shouldFlip = ['arrow-right', 'chevron-right'].includes(name);

  return (
    <Icon
      name={name}
      style={{
        transform: shouldFlip && direction === 'rtl'
          ? 'scaleX(-1)'
          : undefined,
      }}
    />
  );
};
''',
            },
        }

    # =========================================================================
    # CONTENT REVIEW CHECKLIST
    # =========================================================================

    @staticmethod
    def review_checklist() -> Dict[str, List[str]]:
        """Content review checklist for UX writing"""
        return {
            "clarity": [
                "Is the meaning immediately clear?",
                "Are there any ambiguous words?",
                "Would a first-time user understand this?",
                "Is technical jargon avoided or explained?",
            ],
            "conciseness": [
                "Can any words be removed?",
                "Is the message under 2 sentences?",
                "Are there redundant phrases?",
                "Is the CTA 1-3 words?",
            ],
            "helpfulness": [
                "Does it tell users what to do next?",
                "Are error messages actionable?",
                "Is the tone appropriate to the context?",
                "Does it answer 'why should I care?'",
            ],
            "consistency": [
                "Does it match the voice guidelines?",
                "Are terms used consistently?",
                "Does capitalization follow the style guide?",
                "Are similar actions described the same way?",
            ],
            "accessibility": [
                "Does link text describe the destination?",
                "Are instructions not reliant on color/position?",
                "Is alt text meaningful (or empty for decorative)?",
                "Can it be understood by screen reader users?",
            ],
            "localization": [
                "Are there hardcoded strings?",
                "Is there room for text expansion?",
                "Are date/time/currency formats locale-aware?",
                "Is word order flexible for translation?",
            ],
            "inclusivity": [
                "Is gender-neutral language used?",
                "Are ableist terms avoided?",
                "Are cultural assumptions checked?",
                "Are all users represented?",
            ],
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: Severity,
        category: ContentCategory,
        current: str,
        recommended: str,
        rationale: str,
        voice_tone_issue: bool = False,
        accessibility_issue: bool = False,
        localization_issue: bool = False,
    ) -> ContentFinding:
        """Generate a content finding"""
        return ContentFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            current_text=current,
            recommended_text=recommended,
            rationale=rationale,
            voice_tone_issue=voice_tone_issue,
            accessibility_issue=accessibility_issue,
            localization_issue=localization_issue,
        )


def create_enhanced_ux_content_assistant() -> Dict[str, Any]:
    """Factory function to create enhanced UX Content Writer"""
    return {
        "name": "Enhanced UX Content Writer",
        "version": "2.0.0",
        "system_prompt": """Expert UX writer providing guidance on:
- Button and action text patterns (creation, submission, destructive actions)
- Error message frameworks (validation, system errors, tone)
- Empty states and zero-data scenarios
- Loading and progress indicators
- Confirmation dialogs for destructive actions
- Form labels, placeholders, and help text
- Notification and toast patterns
- Onboarding and tutorial content
- Voice and tone guidelines
- Inclusive language standards
- Accessibility text (alt text, ARIA labels, screen reader)
- Localization and internationalization

Reviews microcopy for clarity, conciseness, helpfulness, and consistency.""",
        "assistant_class": EnhancedUXContentAssistant,
        "domain": "content",
        "tags": [
            "ux-writing",
            "microcopy",
            "content-design",
            "accessibility",
            "localization",
            "voice-tone",
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedUXContentAssistant()
    print(f"Version: {assistant.version}")
    print(f"Guidelines: {', '.join(assistant.guidelines)}")
