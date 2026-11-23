import math
import random
import time
import tkinter as tk
from tkinter import font

windowWidth = 940
windowHeight = 820
background = "#000000"
fontFamily = "Segoe UI"
fontSize = 13
fontWeight = "bold"
lineHeight = 25
wordSpacing = 8
fadeTime = 0.46
outlineSpeed = 0.055
insideSpeed = 0.040
centerFade = 1.25

colors = ["#E63946", "#EE424D", "#F34A54", "#F75259", "#FF5B61"]
phrases = [
    "I love you", "Je t'aime", "Te amo", "Ti amo", "Ich liebe dich",
    "Eu te amo", "Te iubesc", "Ik hou van jou", "Seni seviyorum",
    "Jag älskar dig", "Jeg elsker dig", "Kocham cię", "Volim te",
    "Miluji tě", "T'estimo", "Szeretlek", "Aš tave myliu",
    "Aku cinta kamu", "Anh yêu em", "Mahal kita", "Te dua",
    "Я тебя люблю", "Σ' αγαπώ", "愛してる", "我爱你",
    "사랑해", "أحبك", "Ti voglio bene", "Ma armastan sind"
]

root = tk.Tk()
root.title("Love Heart")
root.configure(bg=background)
root.resizable(False, False)

screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
windowX = max(0, (screenWidth - windowWidth) // 2)
windowY = max(0, (screenHeight - windowHeight) // 2)
root.geometry(f"{windowWidth}x{windowHeight}+{windowX}+{windowY}")

canvas = tk.Canvas(root, width=windowWidth, height=windowHeight, bg=background, highlightthickness=0)
canvas.pack()

textFont = font.Font(family=fontFamily, size=fontSize, weight=fontWeight)
centerFont = font.Font(family=fontFamily, size=16, weight=fontWeight)
randomGenerator = random.Random(27)


def heartPoint(angle):
    x = 16 * math.sin(angle) ** 3
    y = 13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle)
    return (windowWidth / 2 + x * 24.0, 367 - y * 19.8)


heartPath = [heartPoint(i * math.tau / 1200) for i in range(1200)]
shortPath = [(i * math.tau / 360, heartPoint(i * math.tau / 360)) for i in range(360)]


def scanline(y):
    intersections = []
    for i in range(len(heartPath)):
        x1, y1 = heartPath[i]
        x2, y2 = heartPath[(i + 1) % len(heartPath)]
        if (y1 <= y < y2) or (y2 <= y < y1):
            intersections.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    intersections.sort()
    return [(intersections[i], intersections[i + 1]) for i in range(0, len(intersections) - 1, 2)]


def commonRanges(first, second):
    ranges = []
    for left1, right1 in first:
        for left2, right2 in second:
            left = max(left1, left2)
            right = min(right1, right2)
            if right - left > 5:
                ranges.append((left, right))
    return ranges


widths = {phrase: textFont.measure(phrase) for phrase in phrases}
shortest = min(widths.values())


def chooseWords(available):
    bestWords = []
    bestRemaining = available
    for attempt in range(22):
        used = 0
        words = []
        while True:
            gap = wordSpacing if words else 0
            remaining = available - used - gap
            choices = [phrase for phrase in phrases if widths[phrase] <= remaining]
            if not choices:
                break
            if remaining > 180:
                compact = [phrase for phrase in choices if widths[phrase] < 142]
                if compact:
                    choices = compact
            recent = words[-2:]
            varied = [phrase for phrase in choices if phrase not in recent]
            if varied:
                choices = varied
            phrase = randomGenerator.choice(choices)
            words.append(phrase)
            used += widths[phrase] + gap
        leftover = available - used
        if words and leftover < bestRemaining:
            bestWords = words
            bestRemaining = leftover
        if bestRemaining < 8:
            break
    return bestWords, bestRemaining


def closestBoundary(x, y):
    closestDistance = float("inf")
    closestAngle = 0.0
    for angle, (px, py) in shortPath:
        distance = (x - px) ** 2 + (y - py) ** 2
        if distance < closestDistance:
            closestDistance = distance
            closestAngle = angle
    return math.sqrt(closestDistance), closestAngle


records = []

for y in range(147, 699, lineHeight):
    heartRanges = scanline(y)
    heartRanges = commonRanges(heartRanges, scanline(y - 9))
    heartRanges = commonRanges(heartRanges, scanline(y + 9))
    for shapeLeft, shapeRight in heartRanges:
        pieces = [(shapeLeft + 4, shapeRight - 4, True, True)]
        if abs(y - 447) < 17:
            adjusted = []
            for left, right, isLeft, isRight in pieces:
                if left < windowWidth / 2 - 90 and right > windowWidth / 2 + 90:
                    adjusted.append((left, windowWidth / 2 - 90, isLeft, False))
                    adjusted.append((windowWidth / 2 + 90, right, False, isRight))
                else:
                    adjusted.append((left, right, isLeft, isRight))
            pieces = adjusted
        for start, end, leftEdge, rightEdge in pieces:
            available = end - start
            if available < shortest:
                continue
            selected, slack = chooseWords(available)
            if not selected:
                continue
            x = start + slack / 2
            for index, phrase in enumerate(selected):
                width = widths[phrase]
                centerX = x + width / 2
                distance, angle = closestBoundary(centerX, y)
                isOutline = (
                    (index == 0 and leftEdge)
                    or (index == len(selected) - 1 and rightEdge)
                    or (distance < 22)
                    or (y <= 172)
                    or (y >= 672)
                )
                records.append({
                    "x": x,
                    "y": y,
                    "phrase": phrase,
                    "angle": angle,
                    "distance": distance,
                    "outline": isOutline,
                    "color": randomGenerator.choice(colors),
                    "duration": fadeTime
                })
                x += width + wordSpacing


outline = [item for item in records if item["outline"]]
inside = [item for item in records if not item["outline"]]

startAngle = 0.91
outline.sort(key=lambda item: (item["angle"] - startAngle) % math.tau)

layers = {}
for item in inside:
    layer = max(0, int(item["distance"] / 28))
    layers.setdefault(layer, []).append(item)

sequence = []
currentTime = 0.48

for item in outline:
    item["start"] = currentTime
    sequence.append(item)
    currentTime += outlineSpeed

currentTime += 0.22

for layerNumber in sorted(layers):
    layerItems = layers[layerNumber]
    layerItems.sort(key=lambda item: (item["angle"] - startAngle) % math.tau, reverse=layerNumber % 2 == 1)
    for item in layerItems:
        item["start"] = currentTime
        sequence.append(item)
        currentTime += insideSpeed
    currentTime += 0.07

currentTime += 0.3
sequence.append({
    "x": windowWidth / 2,
    "y": 447,
    "phrase": "I love you",
    "color": "#FF6A6D",
    "duration": centerFade,
    "start": currentTime,
    "center": True
})

finishTime = currentTime + centerFade


def toRGB(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def blend(first, second, amount):
    amount = max(0, min(1, amount))
    return "#%02x%02x%02x" % tuple(
        round(first[i] + (second[i] - first[i]) * amount)
        for i in range(3)
    )


black = (0, 0, 0)
highlight = toRGB("#FFD0D0")

for item in sequence:
    item["rgb"] = toRGB(item["color"])
    item["id"] = canvas.create_text(
        item["x"], item["y"],
        text=item["phrase"],
        fill=background,
        font=centerFont if item.get("center") else textFont,
        anchor="center" if item.get("center") else "w"
    )

startTime = time.perf_counter()
visibleIndex = 0
fading = []
sparkles = []
nextSparkle = finishTime + 0.6


def restart(event=None):
    global startTime, visibleIndex, fading, sparkles, nextSparkle
    startTime = time.perf_counter()
    visibleIndex = 0
    fading = []
    sparkles = []
    nextSparkle = finishTime + 0.6
    for item in sequence:
        canvas.itemconfigure(item["id"], fill=background)


def animate():
    global visibleIndex, fading, sparkles, nextSparkle
    elapsed = time.perf_counter() - startTime

    while visibleIndex < len(sequence) and sequence[visibleIndex]["start"] <= elapsed:
        fading.append(sequence[visibleIndex])
        visibleIndex += 1

    stillFading = []
    for item in fading:
        progress = (elapsed - item["start"]) / item["duration"]
        if progress >= 1:
            canvas.itemconfigure(item["id"], fill=item["color"])
        else:
            progress = max(0.0, progress)
            progress = progress * progress * (3 - 2 * progress)
            canvas.itemconfigure(item["id"], fill=blend(black, item["rgb"], progress))
            stillFading.append(item)
    fading = stillFading

    if elapsed > finishTime + 0.5:
        if elapsed >= nextSparkle:
            choices = randomGenerator.sample(sequence[:-1], k=min(randomGenerator.choice([1, 1, 2]), len(sequence) - 1))
            currentlyShining = {id(item) for item, start in sparkles}
            for item in choices:
                if id(item) not in currentlyShining:
                    sparkles.append((item, elapsed))
            nextSparkle = elapsed + randomGenerator.uniform(0.24, 0.5)

        stillShining = []
        for item, begin in sparkles:
            progress = (elapsed - begin) / 0.80
            if progress >= 1:
                canvas.itemconfigure(item["id"], fill=item["color"])
            else:
                brightness = math.sin(math.pi * progress) ** 2 * 0.74
                canvas.itemconfigure(item["id"], fill=blend(item["rgb"], highlight, brightness))
                stillShining.append((item, begin))
        sparkles = stillShining

    root.after(25, animate)


root.bind("<r>", restart)
root.bind("<R>", restart)
root.bind("<Escape>", lambda event: root.destroy())
root.after(100, animate)
root.mainloop()
