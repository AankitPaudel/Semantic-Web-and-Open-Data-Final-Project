import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set the visual style for the presentation
sns.set_theme(style="whitegrid")
plt.rcParams['figure.dpi'] = 300  # High resolution for slides
plt.rcParams['font.family'] = 'sans-serif'

def plot_overall_stats():
    """
    Generates Slide 8: The Overall Verdict
    Data source: Analysis 1 from your log
    """
    # Data from your log
    outcomes = ['Home Wins', 'Away Wins', 'Draws']
    percentages = [43.82, 33.82, 22.37]
    colors = ['#2ecc71', '#e74c3c', '#95a5a6']  # Green (Home), Red (Away), Gray (Draw)

    plt.figure(figsize=(10, 6))
    
    # Create Bar Chart
    bars = plt.bar(outcomes, percentages, color=colors, edgecolor='black', alpha=0.8)
    
    # Add title and labels
    plt.title('Premier League Match Outcomes (2020-2024)\nN=1,520 Matches', fontsize=16, pad=20, weight='bold')
    plt.ylabel('Percentage (%)', fontsize=12)
    
    # Add data labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height}%',
                 ha='center', va='bottom', fontsize=14, weight='bold')

    # Add the "Gap" annotation
    plt.annotate('10% Home Advantage Gap\n(Statistically Significant)', 
                 xy=(0.5, 38), xytext=(1.5, 40),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 fontsize=11, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1))

    plt.ylim(0, 55)  # Give some headroom for labels
    plt.tight_layout()
    plt.savefig('overall_advantage.png')
    print("✅ Created 'overall_advantage.png'")
    plt.close()

def plot_team_variance():
    """
    Generates Slide 9: Team Variance (Top 5 vs Bottom 5)
    Data source: Analysis 2 from your log
    """
    # Data from your log: Top 5 Highest Adv + Bottom 5 Lowest Adv
    data = {
        'Team': ['Tottenham', "Nott'm Forest", 'Liverpool', 'Newcastle', 'Wolves', 
                 'Brighton', 'Chelsea', 'Leeds', 'Burnley', 'Watford'],
        'Home_Advantage': [23.68, 21.05, 19.74, 15.79, 14.47, 
                           3.95, 1.32, 0.00, 0.00, -10.53],
        'Group': ['Top 5', 'Top 5', 'Top 5', 'Top 5', 'Top 5', 
                  'Bottom 5', 'Bottom 5', 'Bottom 5', 'Bottom 5', 'Bottom 5']
    }
    
    df = pd.DataFrame(data)
    
    # Sort for visual flow
    df = df.sort_values('Home_Advantage', ascending=True)

    plt.figure(figsize=(12, 8))
    
    # Create Horizontal Bar Chart
    # Color logic: Green for positive, Red for negative
    colors = ['#e74c3c' if x < 0 else '#2ecc71' for x in df['Home_Advantage']]
    
    bars = plt.barh(df['Team'], df['Home_Advantage'], color=colors, edgecolor='black', alpha=0.8)

    # Add vertical line at 0
    plt.axvline(x=0, color='black', linestyle='-', linewidth=1.5)
    plt.axvline(x=9.06, color='gray', linestyle='--', linewidth=1, label='League Average (+9.06%)')

    # Add title and labels
    plt.title('Home Advantage by Team: The "Crowd Effect"\n(Home Win % - Away Win %)', fontsize=16, pad=20, weight='bold')
    plt.xlabel('Percentage Point Difference', fontsize=12)
    
    # Add data labels inside/next to bars
    for bar in bars:
        width = bar.get_width()
        label_x_pos = width + 1 if width >= 0 else width - 3
        plt.text(label_x_pos, bar.get_y() + bar.get_height()/2, 
                 f'{width:+.2f}%', 
                 va='center', fontsize=11, weight='bold')

    # Highlight the anomaly
    plt.annotate('The Anomaly:\nWatford performed WORSE at home', 
                 xy=(-10.53, 0), xytext=(-20, 2),
                 arrowprops=dict(facecolor='red', shrink=0.05),
                 fontsize=10, color='red', weight='bold')

    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig('team_variance.png')
    print("✅ Created 'team_variance.png'")
    plt.close()

if __name__ == "__main__":
    plot_overall_stats()
    plot_team_variance()