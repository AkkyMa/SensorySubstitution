from tkinter import *
from PIL import Image, ImageTk


class Selector(Frame):
    """Selector interface"""

    def set_segment_state(self, segment, state):
        pass

    def get_segment_state(self, segment):
        pass

    def set_segments_code(self, code):
        """Set state of selector segments to state described by given code"""
        pass

    def get_segments_code(self):
        """Get code which describe state of selector segments"""
        pass

    def set_default(self):
        """Set selector segments to default state"""
        pass

    def callback_after_click(self, segment):
        """Calls after click processed
        :param segment: segment was changed by click. None if nothing was changed.
        """
        pass

class Segment14(Selector):

    """Selector for 14 segment board

    Data format:

    Segments designate by letters which corresponds to next segments on board:
                 AAAAAAAAA
                FH   J   KB
                F H  J  K B
                F  H J K  B
                F   HJK   B
                 G1G1 G2G2
                E   LMN   C
                E  L M N  C
                E L  M  N C
                EL   M   NC
                 DDDDDDDDD

    Segments code is integer which bits describe state of each segment. Segments order corresponds to lexicographical order
    """

    _segments = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G1': 6, 'G2': 7, 'H': 8, 'J': 9, 'K': 10, 'L': 11,
                 'M': 12, 'N': 13}

    def __init__(self, master=None, cnf={},
                 width=283, height=283,
                 background='lightgray', enable_color='red', disable_color='red4',
                 **kw):
        """For parameter overview look config description"""

        super().__init__(master, cnf, **kw)

        self._segment_states = {c: False for c in self._segments}
        self._segment_ids = {c: None for c in self._segments}

        self._segment_files_original = dict()
        for c in self._segments:
            self._segment_files_original[c] = Image.open("segments\\" + c + ".bmp")

        self._canvas = Canvas(self, highlightthickness=0)
        self._canvas.grid()
        self._canvas.bind('<Button-1>', self._on_click)

        self.config(width=width, height=height, background=background, enable_color=enable_color, disable_color=disable_color)

    def config(self, width=None, height=None, background=None, enable_color=None, disable_color=None):
        """ Configure selector
        :param background: tkinter color for selector background
        :param enable_color: tkinter color for active segment
        :param disable_color: tkinter color for inactive segment
        """
        redraw_need = False
        if width is not None:
            self._width = width
            redraw_need = True
        if height is not None:
            self._height = height
            redraw_need = True
        if background is not None:
            self._canvas.config(background=background)
        if enable_color  is not None:
            self._color_on = enable_color
            redraw_need = True
        if disable_color is not None:
            self._color_off = disable_color
        if redraw_need:
            self._redraw()

    def _redraw(self):

        self._canvas.config(width=self._width, height=self._height)

        segment_files_scaled = dict()
        for c in self._segments:
            segment_files_scaled[c] = self._segment_files_original[c].resize((self._width, self._height))

        self._segment_images_off = dict()
        for c in self._segments:
            self._segment_images_off[c] = ImageTk.BitmapImage(segment_files_scaled[c], foreground=self._color_off)

        self._segment_images_on = dict()
        for c in self._segments:
            self._segment_images_on[c] = ImageTk.BitmapImage(segment_files_scaled[c], foreground=self._color_on)

        self._segment_maps = dict()
        for c in self._segments:
            self._segment_maps[c] = segment_files_scaled[c].getdata()

        for c in self._segments:
            self._redraw_segment(c)

    def _redraw_segment(self, segment):
        self._canvas.delete(self._segment_ids[segment])
        self._segment_ids[segment] = self._canvas.create_image(0, 0,
                                                               image=self._segment_images_on[segment]
                                                               if self._segment_states[segment]
                                                               else self._segment_images_off[segment],
                                                               anchor=NW)

    def set_segment_state(self, segment, state):
        if self._segment_states[segment] is not state:
            self._segment_states[segment] = state
            self._redraw_segment(segment)

    def get_segment_state(self, segment):
        return self._segment_states[segment]

    def set_segments_code(self, code):
        for c in self._segments:
            self.set_segment_state(c, code >> self._segments[c] & 1)

    def get_segments_code(self):
        code = 0
        for c in self._segments:
            code |= self._segment_states[c] << self._segments[c]
        return code

    def _on_click(self, event):
        segment = None
        for segment in self._segments:
            if self._segment_maps[segment][event.y*self._width + event.x] == 255:
                self._segment_states[segment] = not self._segment_states[segment]
                self._redraw_segment(segment)
        self.callback_after_click(segment)


class CircleSegments(Selector):

    """
        General selector for boards with circle segments

        Data format:
        Segments numbered from left to right, from up to down
        Segments code is integer which bits describe segment states respect to order written above
    """

    def __init__(self, horizontal_segments, vertical_segments,
                 master=None, cnf={},
                 width=None, height=None,
                 background='lightgray',
                 enable_color='red',
                 disable_color='red4',
                 segment_size_coefficient=0.4,
                 clickable=True,
                 **kw):
        """
        :param horizontal_segments: number of horizontal segments
        :param vertical_segments: number of vertical segments
        For rest parameters look config()
        """

        super().__init__(master, cnf, **kw)

        if width is None and height is None:
            if horizontal_segments > vertical_segments:
                width = 283
            else:
                height = 283

        self._segments_hor = horizontal_segments
        self._segments_ver = vertical_segments
        self._segments = vertical_segments * horizontal_segments

        self._segment_states = [False for c in range(self._segments)]
        self._segment_ids = list()
        self._id_to_index = dict()

        self._canvas = Canvas(self, highlightthickness=0)
        self._canvas.pack()

        self.config(width, height, background=background, enable_color=enable_color, disable_color=disable_color,
                    segment_size_coefficient=segment_size_coefficient, clickable=clickable)

    def config(self, width=None, height=None, background=None, enable_color=None, disable_color=None,
               segment_size_coefficient=None, clickable=None, **kw):
        """ Configure selector.
        :param height, width: height and width of widget. Left empty for standart size. Point one to let widget calculate second to save proportions.
               Point both to strictly define size. Note for good proportions of segments proportion of width x height
               should be 1x1 if you don't use disablable lines and 5x6 if you do.
        :param background: tkinter color of background
        :param enable_color: tkinter color of active segment
        :param disable_color: tkinter color of inactive segment
        :param segment_size_coefficient: coefficient of segment size on canvas. 0 - infinity small, 1 - segment touch
               each other
        :param clickable: If selector should be clickable
        """
        redraw_need = False
        repaint_need = False

        if width is not None or height is not None:
            if width is not None and height is not None:
                self._width = width
                self._height = height
            elif width is not None and height is None:
                self._width = width
                self._height = width / self._segments_hor * self._segments_ver
            elif width is None and height is not None:
                self._width = height / self._segments_ver * self._segments_hor
                self._height = height
            redraw_need = True

        if background is not None:
            self._canvas.config(background=background)
            kw['background'] = background
        if enable_color is not None:
            self._color_on = enable_color
            repaint_need = True
        if disable_color is not None:
            self._color_off = disable_color
            repaint_need = True
        if segment_size_coefficient is not None:
            if segment_size_coefficient > 1:
                raise ValueError("Size coefficient must not be bigger than 1")
            self._segment_size_coefficient = segment_size_coefficient
            redraw_need = True
        if clickable is not None:
            if clickable:
                self._canvas.bind('<Button-1>', self._on_click)
            else:
                self._canvas.unbind('<Button-1>')
        if len(kw) > 0:
            super().config(**kw)

        if redraw_need:
            self._redraw()
        elif repaint_need:
            self._repaint()

    def set_segment_state(self, segment, state):
        """ Set state of segment
        :param segment: int - absolute value of segment, tuple - (x, y) coordinate of segment
        """
        if type(segment) is tuple:
            segment = self._coord_to_index(segment)
        self._segment_states[segment] = state
        self._repaint_segment(segment)

    def get_segment_state(self, segment):
        """ Get state of segment
        :param segment: int - absolute value of segment, tuple - (x, y) coordinate of segment
        """
        if type(segment) is tuple:
            segment = self._coord_to_index(segment)
        return self._segment_states[segment]

    def set_segments_code(self, code):
        for segment_index in range(self._segments):
            self.set_segment_state(segment_index, code >> segment_index & 1)

    def get_segments_code(self):
        code = 0
        for segment_index in range(self._segments):
            code |= self._segment_states[segment_index] << segment_index
        return code

    def set_default(self):
        self.set_segments_code(0)

    def _redraw(self):
        self._canvas.config(width=self._width, height=self._height)

        space_x = self._width / self._segments_hor
        space_y = self._height / self._segments_ver
        radius_x = space_x / 2 * self._segment_size_coefficient
        radius_y = space_y / 2 * self._segment_size_coefficient

        for segment_id in self._segment_ids:
            self._canvas.delete(segment_id)
        self._segment_ids.clear()
        self._id_to_index.clear()
        for y in range(self._segments_ver):
            for x in range(self._segments_hor):
                centre_x = space_x * (x+0.5)
                centre_y = space_y * (y+0.5)
                segment_index = self._coord_to_index((x, y))
                segment_id = self._canvas.create_oval(centre_x - radius_x, centre_y - radius_y,
                                                      centre_x + radius_x, centre_y + radius_y,
                                                      fill=self._color_on if self._segment_states[segment_index]
                                                      else self._color_off)
                self._segment_ids.append(segment_id)
                self._id_to_index[segment_id] = segment_index

    def _repaint(self):
        for segment in range(self._segments):
            self._repaint_segment(segment)

    def _repaint_segment(self, segment):
        segment_id = self._segment_ids[segment]
        self._canvas.itemconfig(segment_id, fill=self._color_on if self._segment_states[segment] else self._color_off)

    def _coord_to_index(self, coord):
        return coord[1] * self._segments_hor + coord[0]

    def _on_click(self, event):
        segment_index = None
        result = self._canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if len(result) is 1:
            segment_id = result[0]
            segment_index = self._id_to_index[segment_id]
            self._segment_states[segment_index] = not self._segment_states[segment_index]
            self._repaint_segment(segment_index)
        self.callback_after_click(segment_index)


class Arrows(Selector):

    """Selector of up-directed arrow segments
    Segments numbered from left to right
    Segments code is integer which bits describe segment states respect to order written above
    """

    def __init__(self, segment_number,
                 master=None, cnf={},
                 width=None, height=None,
                 background='lightgray',
                 enable_color='red',
                 disable_color='red4',
                 segment_size_coefficient=0.5,
                 clickable=True,
                 **kw):
        if (width is None and height is None):
            width = 283

        super().__init__(master, cnf, **kw)

        self._segment_ids = list()
        self._id_to_index = dict()
        self._segments = segment_number
        self._segment_states = [True for c in range(self._segments)]
        self._canvas = Canvas(self, highlightthickness=0)
        self._canvas.pack()

        self.config(width=width, height=height, background=background, enable_color=enable_color,
                    disable_color=disable_color, segment_size_coefficient=segment_size_coefficient, clickable=clickable)

    def config(self, width=None, height=None, background=None, enable_color=None, disable_color=None,
               segment_size_coefficient=None, clickable=None):
        """ Configure selector.
        :param height, width: height and width of widget. Left empty for standart size. Point one to let widget calculate second to save proportions.
               Point both to strictly define size. Note for good proportions of segments proportion of width x height
               should be 1x1 if you don't use disablable lines and 5x6 if you do.
        :param background: tkinter color of background
        :param enable_color: tkinter color of active segment
        :param disable_color: tkinter color of inactive segment
        :param segment_size_coefficient: coefficient of segment size on canvas. 0 - infinity small, 1 - segment touch
               each other
        :param clickable: If selector should be clickable
        """

        redraw_need = False
        repaint_need = False

        if width is not None or height is not None:
            if width is not None and height is not None:
                self._width = width
                self._height = height
            elif width is not None and height is None:
                self._width = width
                self._height = width / self._segments
            elif width is None and height is not None:
                self._width = self._segments * height
                self._height = height
            redraw_need = True
        if background is not None:
            self._canvas.config(background=background)
        if enable_color is not None:
            self._color_on = enable_color
            repaint_need = True
        if disable_color is not None:
            self._color_off = disable_color
            repaint_need = True
        if segment_size_coefficient is not None:
            if segment_size_coefficient > 1:
                raise ValueError("Size coefficient must not be bigger than 1")
            self._size_coef = segment_size_coefficient
            redraw_need = True
        if clickable is not None:
            if clickable:
                self._canvas.bind('<Button-1>', self._on_click)
            else:
                self._canvas.unbind('<Button-1>')

        if redraw_need:
            self._redraw()
        elif repaint_need:
            self._repaint()

    def set_segment_state(self, segment, state):
        self._segment_states[segment] = state
        self._repaint_segment(segment)

    def get_segment_state(self, segment):
        return self._segment_states[segment]

    def set_segments_code(self, code):
        for segment in range(self._segments):
            state = code >> segment & 1
            self.set_segment_state(segment, state)

    def get_segments_code(self):
        code = 0
        for segment in range(self._segments):
            code |= self.get_segment_state(segment) << segment
        return code

    def set_default(self):
        self.set_segments_code(-1)

    def _redraw(self):
        self._canvas.config(width=self._width, height=self._height)

        space_x = self._width / self._segments
        space_y = self._height
        center_y = space_y / 2
        bias_x = space_x / 2 * self._size_coef
        bias_y = space_y / 2 * self._size_coef

        for segment_id in self._segment_ids:
            self._canvas.delete(segment_id)
        self._segment_ids.clear()
        self._id_to_index.clear()
        for segment_index in range(self._segments):
            center_x = (segment_index+0.5) * space_x
            segment_id = self._canvas.create_polygon(center_x, center_y-bias_y,
                                                   center_x-bias_x, center_y+bias_y,
                                                   center_x+bias_x, center_y+bias_y,
                                                   fill=self._color_on if self._segment_states[segment_index] else self._color_off)
            self._segment_ids.append(segment_id)
            self._id_to_index[segment_id] = segment_index

    def _repaint(self):
        for segment in range(self._segments):
            self._repaint_segment(segment)

    def _repaint_segment(self, segment):
        segment_id = self._segment_ids[segment]
        self._canvas.itemconfig(segment_id, fill=self._color_on if self._segment_states[segment] else self._color_off)

    def _on_click(self, event):
        segment_index = None
        result = self._canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if len(result) is 1:
            segment_id = result[0]
            segment_index = self._id_to_index[segment_id]
            self._segment_states[segment_index] = not self._segment_states[segment_index]
            self._repaint_segment(segment_index)
        self.callback_after_click(segment_index)


class CircleSegmentsDisablableLines(Selector):

    """General selector for board with circle segments with opportunity disable unused lines"""

    def __init__(self,
                 lines, segments_in_line,
                 master=None, cnf={},
                 width=None, height=None,
                 background='lightgrey',
                 enable_color='red', disable_color='red4',
                 segment_size_coefficient=0.4,
                 clickable=True,
                 **kw):
        """For keyword description look config"""
        super().__init__(master, cnf, **kw)

        if width is None and height is None:
            if lines > segments_in_line:
                width = 283
            else:
                height = 283

        self._lines = lines
        self._seg_in_line = segments_in_line
        self._segments = lines * segments_in_line

        self._segments = CircleSegments(lines, segments_in_line, master=self)
        self._segments.grid(row=1)
        self._segments._on_click = self._on_segments_click
        self._arrows = Arrows(lines, master=self)
        self._arrows.grid(row=2)
        self._arrows._on_click = self._on_arrows_click

        self.set_segment_state = self._segments.set_segment_state
        self.get_segment_state = self._segments.get_segment_state
        self.set_segments_code = self._segments.set_segments_code
        self.get_segments_code = self._segments.get_segments_code
        self.set_line_state = self._arrows.set_segment_state
        self.get_line_state = self._segments.get_segment_state
        self.set_lines_code = self._arrows.set_segments_code
        self.get_lines_code = self._arrows.get_segments_code

        self.config(width, height, background, enable_color, disable_color, segment_size_coefficient, clickable)

    def config(self, width=None, height=None, background=None, enable_color=None, disable_color=None,
               segment_size_coefficient=None, clickable=None):
        """ Configure selector.
        :param height, width: height and width of widget. Left empty for standart size. Point one to let widget calculate second to save proportions.
               Point both to strictly define size. Note for good proportions of segments proportion of width x height
               should be 1x1 if you don't use disablable lines and 5x6 if you do.
        :param background: tkinter color of background
        :param enable_color: tkinter color of active segment
        :param disable_color: tkinter color of inactive segment
        :param segment_size_coefficient: coefficient of segment size on canvas. 0 - infinity small, 1 - segment touch
               each other
        :param clickable: If selector should be clickable
        """

        if segment_size_coefficient is not None:
            seg_size_coefficient = segment_size_coefficient
            arrow_size_coefficient = segment_size_coefficient * 13/10
            if arrow_size_coefficient > 1:
                arrow_size_coefficient = 1
        else:
            seg_size_coefficient = None
            arrow_size_coefficient = None

        if height is not None:
            segments_height = height * self._seg_in_line / (self._seg_in_line+1)
            arrows_height = height / (self._seg_in_line + 1)
        else:
            segments_height = None
            arrows_height = None

        self._segments.config(width=width, height=segments_height, background=background, enable_color=enable_color,
                              disable_color=disable_color, segment_size_coefficient=seg_size_coefficient, clickable=clickable)
        self._arrows.config(width=width, height=arrows_height, background=background, enable_color=enable_color,
                            disable_color=disable_color, segment_size_coefficient=arrow_size_coefficient, clickable=clickable)

    def set_default(self):
        self._segments.set_default()
        self._arrows.set_default()

    def _on_segments_click(self, event):
        arrow_index = None
        result = self._segments._canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if len(result) is 1:
            segment_id = result[0]
            segment_index = self._segments._id_to_index[segment_id]
            line = segment_index % self._lines
            if self._arrows.get_segment_state(line):
                self._segments._segment_states[segment_index] = not self._segments._segment_states[segment_index]
                self._segments._repaint_segment(segment_index)
        self.callback_after_click(arrow_index)

    def _on_arrows_click(self, event):
        arrow_index = None
        result = self._arrows._canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if len(result) is 1:
            arrow_id = result[0]
            arrow_index = self._arrows._id_to_index[arrow_id]
            self._arrows._segment_states[arrow_index] = not self._arrows._segment_states[arrow_index]
            self._arrows._repaint_segment(arrow_index)
            for y in range(self._seg_in_line):
                self._segments.set_segment_state((arrow_index, y), False)
        self.callback_after_click(arrow_index)