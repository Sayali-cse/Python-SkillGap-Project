import matplotlib.pyplot as plt


class ChartBuilder:
    """Job: draw the charts."""

    def readiness_donut(self, percent):
        if percent >= 80:
            color = "#22C55E"       # green
        elif percent >= 50:
            color = "#F59E0B"       # orange
        else:
            color = "#EF4444"       # red

        fig, ax = plt.subplots(figsize=(3.4, 3.4))
        ax.pie([percent, 100 - percent], colors=[color, "#E5E7EB"], startangle=90,
               counterclock=False, wedgeprops={"width": 0.28})
        ax.text(0, 0.06, str(percent) + "%", ha="center", va="center",
                fontsize=28, fontweight="bold")
        ax.text(0, -0.28, "Job Readiness", ha="center", fontsize=10, color="gray")
        return fig

    def level_comparison(self, results):
        names = []
        your_pos = []
        your_level = []
        req_pos = []
        req_level = []
        for i in range(len(results)):
            names.append(results[i]["skill"])
            your_pos.append(i - 0.2)
            your_level.append(results[i]["level"])
            req_pos.append(i + 0.2)
            req_level.append(results[i]["required"])

        fig, ax = plt.subplots(figsize=(6.5, 3.4))
        ax.barh(your_pos, your_level, height=0.35, color="#6C63FF", label="Your Level")
        ax.barh(req_pos, req_level, height=0.35, color="#F59E0B", label="Required Level")
        ax.set_yticks(range(len(results)))
        ax.set_yticklabels(names)
        ax.invert_yaxis()
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(["Basic", "Intermediate", "Advanced"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=2)
        fig.tight_layout()
        return fig
