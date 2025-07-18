import QtQuick 2.15
import QtQuick.Controls 2.15
// import QtQuick.Controls.Material 2.15


Rectangle {
    width: 120
    height: 40
    // background: rgba(0, 0, 0, 0)
    // opacity: 0
    clip: true
    // color: "tomato"
    color: "#31363b"

    Switch {
        anchors.centerIn: parent
        text: "amd mode"
        checked: false
        onToggled: backend.toggle_feature(checked)
    }
}

