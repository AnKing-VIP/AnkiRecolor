/* global Recolor */

window.Recolor = {}
Recolor.withConfig = function (confstr) {
  const conf = JSON.parse(confstr)
  const colors = conf.colors
  for (const colorName in colors) {
    const colorEntry = colors[colorName]
    const cssColorName = colorEntry[3]
    const dayColor = colorEntry[1]
    document.documentElement.style.setProperty(cssColorName, dayColor)
  }
}
