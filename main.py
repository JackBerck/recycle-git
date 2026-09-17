import os
import sys
import delete_repos
import delete_vercel_projects

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        clear_screen()
        print("=" * 60)
        print(" ♻️   RECYCLE-GIT: BATCH RESOURCE CLEANUP TOOL")
        print("=" * 60)
        print("\nSelect a service to cleanup:\n")
        print(" [1] 🐙 GitHub Repositories Deleter")
        print(" [2] 📐 Vercel Projects Deleter")
        print(" [q] 🚪 Exit")
        print("\n" + "=" * 60)
        
        choice = input("👉 Enter choice (1/2/q): ").strip().lower()
        
        if choice == '1':
            try:
                delete_repos.main()
            except KeyboardInterrupt:
                print("\n\nOperation interrupted.")
        elif choice == '2':
            try:
                delete_vercel_projects.main()
            except KeyboardInterrupt:
                print("\n\nOperation interrupted.")
        elif choice in ['q', 'quit', 'exit']:
            print("\nGoodbye! 👋")
            break
        else:
            input("\n❌ Invalid choice. Press Enter to try again...")

if __name__ == "__main__":
    main()
