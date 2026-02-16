#!/bin/bash
# .agent/scripts/parallel_session.sh
# Protocol 409: Parallel Worktree Orchestration
# 
# Usage:
#   ./parallel_session.sh create [session_id]
#   ./parallel_session.sh list
#   ./parallel_session.sh remove <session_id>
#   ./parallel_session.sh status

set -e

ACTION=$1
SESSION_ID=${2:-$(date +%s)}
WORKTREE_BASE="../.worktrees"
PROJECT_ROOT=$(git rev-parse --show-toplevel)

case $ACTION in
  create)
    echo "🔀 Creating worktree for session $SESSION_ID..."
    mkdir -p "$WORKTREE_BASE"
    
    # Create branch and worktree
    git worktree add "$WORKTREE_BASE/session-$SESSION_ID" -b "feature/session-$SESSION_ID"
    
    echo "✅ Created worktree: $WORKTREE_BASE/session-$SESSION_ID"
    echo "📍 Branch: feature/session-$SESSION_ID"
    echo ""
    echo "To work in this session:"
    echo "  cd $WORKTREE_BASE/session-$SESSION_ID"
    ;;
  
  list)
    echo "📋 Active worktrees:"
    git worktree list
    echo ""
    echo "Session worktrees:"
    for dir in "$WORKTREE_BASE"/session-*/; do
      if [ -d "$dir" ]; then
        session=$(basename "$dir")
        branch=$(cd "$dir" && git branch --show-current)
        echo "  • $session → $branch"
      fi
    done
    ;;
  
  remove)
    if [ -z "$2" ]; then
      echo "❌ Usage: parallel_session.sh remove <session_id>"
      exit 1
    fi
    
    echo "🗑️  Removing worktree for session $SESSION_ID..."
    
    # Remove worktree
    git worktree remove "$WORKTREE_BASE/session-$SESSION_ID" --force 2>/dev/null || true
    
    # Remove branch
    git branch -D "feature/session-$SESSION_ID" 2>/dev/null || true
    
    echo "✅ Removed worktree and branch for session-$SESSION_ID"
    ;;
  
  status)
    echo "📊 Worktree Status:"
    echo ""
    
    for dir in "$WORKTREE_BASE"/session-*/; do
      if [ -d "$dir" ]; then
        session=$(basename "$dir")
        branch=$(cd "$dir" && git branch --show-current)
        changes=$(cd "$dir" && git status --porcelain | wc -l | tr -d ' ')
        ahead=$(cd "$dir" && git rev-list HEAD ^origin/main --count 2>/dev/null || echo "?")
        
        echo "Session: $session"
        echo "  Branch: $branch"
        echo "  Uncommitted changes: $changes"
        echo "  Commits ahead of main: $ahead"
        echo ""
      fi
    done
    ;;
  
  merge)
    if [ -z "$2" ]; then
      echo "❌ Usage: parallel_session.sh merge <session_id>"
      exit 1
    fi
    
    echo "🔀 Merging session $SESSION_ID into main..."
    
    # Ensure we're on main
    git checkout main
    git pull --rebase
    
    # Merge the session branch
    git merge "feature/session-$SESSION_ID" --no-ff -m "Merge session $SESSION_ID"
    
    echo "✅ Merged session $SESSION_ID into main"
    echo "💡 Run 'parallel_session.sh remove $SESSION_ID' to clean up"
    ;;
  
  *)
    echo "Parallel Session Manager (Protocol 409)"
    echo ""
    echo "Usage: parallel_session.sh {create|list|remove|status|merge} [session_id]"
    echo ""
    echo "Commands:"
    echo "  create [id]  Create a new worktree for parallel work"
    echo "  list         List all active worktrees"
    echo "  remove <id>  Remove a worktree and its branch"
    echo "  status       Show status of all session worktrees"
    echo "  merge <id>   Merge a session branch into main"
    exit 1
    ;;
esac
