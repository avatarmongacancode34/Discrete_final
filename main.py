"""
Main entry point for Traffic Light Fuzzy Logic System

This module provides options to:
1. Run the traffic simulation
2. Visualize fuzzy membership functions
3. Test fuzzy inference with custom inputs
"""
import sys
from fuzzy_controller import TrafficLightController
from traffic_simulation import TrafficSimulation


def show_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("  FUZZY LOGIC TRAFFIC LIGHT CONTROL SYSTEM")
    print("="*60)
    print("\n1. Run Traffic Simulation")
    print("2. Visualize Fuzzy Membership Functions")
    print("3. Test Fuzzy Inference (Custom Inputs)")
    print("4. Run All Visualizations")
    print("5. Exit")
    print("\n" + "="*60)


def run_simulation():
    """Run the main traffic simulation"""
    print("\nStarting traffic simulation...")
    print("Random spawn rates will be generated for each direction")
    print("Close the window to return to menu\n")
    
    try:
        sim = TrafficSimulation()
        sim.run()
    except Exception as e:
        print(f"Error running simulation: {e}")


def visualize_membership_functions():
    """Show fuzzy membership function graphs"""
    print("\nGenerating membership function visualizations...")
    controller = TrafficLightController("demo")
    controller.visualize_membership_functions()
    print("Visualization complete!")


def test_fuzzy_inference():
    """Test fuzzy inference with user inputs"""
    print("\n" + "-"*60)
    print("  FUZZY INFERENCE TESTING")
    print("-"*60)
    
    controller = TrafficLightController("test")
    
    # Predefined test cases
    test_cases = [
        (20, 25, "Low density, short wait"),
        (50, 60, "Medium density, medium wait"),
        (85, 95, "High density, long wait"),
        (30, 80, "Low-medium density, long wait"),
        (70, 40, "High density, medium wait"),
    ]
    
    print("\nRunning predefined test cases:\n")
    for density, wait, description in test_cases:
        green_time = controller.compute_green_time(density, wait)
        print(f"  {description}")
        print(f"  → Input: Density={density}%, Wait={wait}s")
        print(f"  → Output: Green Light={green_time}s\n")
    
    # Interactive testing
    print("\nInteractive Testing (enter 'q' to quit)")
    print("-"*60)
    
    while True:
        try:
            density_input = input("\nEnter traffic density (0-100) or 'q' to quit: ")
            if density_input.lower() == 'q':
                break
            
            wait_input = input("Enter average wait time (0-120 seconds): ")
            
            density = float(density_input)
            wait_time = float(wait_input)
            
            if not (0 <= density <= 100):
                print("Density must be between 0 and 100!")
                continue
            
            if not (0 <= wait_time <= 120):
                print("Wait time must be between 0 and 120 seconds!")
                continue
            
            green_time = controller.compute_green_time(density, wait_time)
            
            print(f"\n  RESULT:")
            print(f"  Input: Density={density}%, Wait={wait_time}s")
            print(f"  Output: Green Light Duration={green_time}s")
            
            viz = input("\nVisualize this inference? (y/n): ")
            if viz.lower() == 'y':
                controller.visualize_inference(density, wait_time)
        
        except ValueError:
            print("Invalid input! Please enter numeric values.")
        except Exception as e:
            print(f"Error: {e}")


def run_all_visualizations():
    """Generate all visualization graphs"""
    print("\nGenerating all visualizations...")
    
    controller = TrafficLightController("demo")
    
    # 1. Membership functions
    print("\n1. Generating membership functions...")
    controller.visualize_membership_functions("membership_functions.png")
    
    # 2. Inference examples
    print("2. Generating inference examples...")
    
    test_cases = [
        (20, 25, "Low density, short wait"),
        (50, 60, "Medium density, medium wait"),
        (85, 95, "High density, long wait"),
    ]
    
    for i, (density, wait, description) in enumerate(test_cases, 1):
        print(f"   - {description}")
        green_time = controller.compute_green_time(density, wait)
        controller.visualize_inference(density, wait, f"inference_example_{i}.png")
        print(f"     Result: {green_time}s green time")
    
    print("\nAll visualizations complete!")
    print("Files saved to current directory")


def main():
    """Main entry point"""
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                run_simulation()
            elif choice == '2':
                visualize_membership_functions()
            elif choice == '3':
                test_fuzzy_inference()
            elif choice == '4':
                run_all_visualizations()
            elif choice == '5':
                print("\nExiting... Goodbye!")
                sys.exit(0)
            else:
                print("\nInvalid choice! Please enter 1-5.")
        
        except KeyboardInterrupt:
            print("\n\nExiting... Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()