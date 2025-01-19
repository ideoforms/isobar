class MPENote:
    def __init__(self,
                 note: int,
                 channel: int,
                 output_device):
        self.note = note
        self.channel = channel
        self.output_device = output_device

        # When the note is released, `is_down` is set to False.
        self.is_down = True

    def pitch_bend(self, pitch: int = 0) -> None:
        if self.is_down:
            self.output_device.pitch_bend(pitch, channel=self.channel)

    def aftertouch(self, value: int = 0) -> None:
        if self.is_down:
            self.output_device.aftertouch(value, channel=self.channel)

    def control(self, control: int = 0, value: int = 0) -> None:
        if self.is_down:
            self.output_device.control(control, value, channel=self.channel)

    def note_off(self) -> None:
        if self.is_down:
            self.output_device.note_off(self.note)