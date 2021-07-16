/* global Recolor */

window.Recolor = {}
Recolor.withConfig = function (confstr, colorIdx) {
  const conf = JSON.parse(confstr)
  const colors = conf.colors
  for (const colorName in colors) {
    const colorEntry = colors[colorName]
    const cssColorName = colorEntry[3]
    const colorHex = colorEntry[colorIdx]
    document.documentElement.style.setProperty(cssColorName, colorHex)
  }
}
