import os

def main():
    while True:
        print("\n🚦 POTHOLE DETECTION SYSTEM 🚦")
        print("1. Run with default video (test.mp4)")
        print("2. Run with custom video file (same folder)")
        print("3. Run with full video path")
        print("4. Run with webcam (0)")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            os.system("python pothole_detection.py --source test.mp4")

        elif choice == "2":
            video_file = input("Enter video filename (e.g., road.mp4): ")
            if os.path.exists(video_file):
                os.system(f"python pothole_detection.py --source {video_file}")
            else:
                print(f"❌ File '{video_file}' not found in current folder.")

        elif choice == "3":
            video_path = input("Enter full video path (e.g., C:/Users/You/Videos/road.mp4): ")
            if os.path.exists(video_path):
                os.system(f"python pothole_detection.py --source \"{video_path}\"")
            else:
                print(f"❌ File not found at '{video_path}'.")

        elif choice == "4":
            os.system("python pothole_detection.py --source 0")

        elif choice == "5":
            print("✅ Exiting...")
            break

        else:
            print("⚠ Invalid choice! Please try again.")


if __name__ == "__main__":
    main()
