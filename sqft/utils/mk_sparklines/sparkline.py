from PIL import Image, ImageDraw, ImageFont

faded_color = (200, 204, 190)
sharp_color = (118, 177, 37)

f = ImageFont.truetype("Helvetica.ttf", 12)

#draw pointer
for j in range(0, 101):
    i = Image.new("RGB", (187, 28), (255,255,255))
    d = ImageDraw.Draw(i)

    startx = 10
    endx = 170
    y = 22

    d.line((startx, y, endx, y), fill=faded_color)
    d.polygon([(startx, y-3), (startx, y+3), (startx-3, y)], fill=faded_color)
    d.polygon([(endx, y-3), (endx, y+3), (endx+3, y)], fill=faded_color)
    if j > 10: d.text((startx-5, y-18), "$", font=f, fill=faded_color)
    if j < 90: d.text((endx-12, y-18), "$$$", font=f, fill=faded_color)

    #find 35% of the line between startx and endx
    p = startx + ((endx - startx) * (float(j)/100))
    #draw a pointer there
    d.polygon([(p, y-1), (p-3, y-5), (p+3, y-5)], fill=sharp_color)
    #and draw the pct above
    h, w = map(float, d.textsize("%s%%" % j, font=f))
    d.text((p-(w*.85), y-18), "%s%%" % j, font=f, fill=sharp_color)

    i.save("../../../static/img/pctlines/sparkline%s.gif" % j)
