import numpy as np
import re
import matplotlib.path as mplt_path
# import source.filbehandling.make_objects as mo


def prepare_angel(angel):
    if not -1 < angel / 360 < 1:
        if angel % 360 != 0:
            angel = angel % 360
        else:
            angel = 0
    if 89.99999 < angel < 90.00001 or -89.99999 > angel > -90.00001:
        angel = 89.99999
    elif 269.99999 < angel < 270.00001 or -269.99999 > angel > -270.00001:
        angel = 269.99999
    return angel


def prep_points_tunnel_boundary(points_tunnel_boundary0, data, index_boundary1):
    points_tunnel_boundary = []
    for index, points in enumerate(points_tunnel_boundary0):
        data[index_boundary1 + index] = re.sub(r'^(\s*(?:\S+\s+){0})\S+', r'\1 ' + str(index) + ':',
                                               data[index_boundary1 + index])
        points_string = re.findall(r"[-+]?(?:\d*\.\d+|\d+\b(?!:))", points)
        points = [float(points_string[0]), float(points_string[1])]
        points_tunnel_boundary.append(points)
    return points_tunnel_boundary


class InnerBoundary:
    # inner boundary er en class der hensikten er å tilordne korrekt plassering for de indre punktene som beskriver
    # svakhetssonen i rs2. Dette skal kun inntreffe hvis sonen treffer tunnelen. Med andre ord, denne classen må ta
    # høyde for situasjon der enten 0, 1, 2 etc. linjeelement treffer tunnelåpningen.
    def __init__(self, ant_linjer, nth_quad, punkter_ytre, data, number_points_inner_boundary, index_boundary1,
                 diameter, vinkel, points_tunnel_boundary):
        self.nth_quad = nth_quad
        self.punkter_ytre = punkter_ytre.copy()
        self.data = data
        self.n_points_ib = number_points_inner_boundary
        self.index_boundary1 = index_boundary1
        self.ant_linjer = ant_linjer
        self.diameter = diameter
        self.vinkel = vinkel
        self.points_tunnel_boundary = points_tunnel_boundary.copy()
        path = mplt_path.Path(points_tunnel_boundary)
        inside = path.contains_points(self.get_middle_points())
        if any(inside):
            self.inner_points = True
        else:
            self.inner_points = False

    def get_middle_points(self):
        p = []
        for i in range(self.ant_linjer):
            k = [3, 1]
            p.append(((self.punkter_ytre[i][0] + self.punkter_ytre[i + k[i]][0]) / 2,
                      (self.punkter_ytre[i][1] + self.punkter_ytre[i + k[i]][1]) / 2))
        return p

    @staticmethod
    def which_quad(punkt):
        if punkt[0] > 0 and punkt[1] >= 0:
            return '1st quad'
        elif punkt[0] <= 0 and punkt[1] > 0:
            return '2nd quad'
        elif punkt[0] < 0 and punkt[1] <= 0:
            return '3rd quad'
        elif punkt[0] >= 0 and punkt[1] < 0:
            return '4th quad'
        else:
            return None

    def get_quad_index(self, punkt):
        switcher = {
            '4th quad': 0,
            '1st quad': 1,
            '2nd quad': 2,
            '3rd quad': 3,
        }
        return switcher.get(self.which_quad(punkt), None)

    @staticmethod
    def which_outer_boundary_point(element):
        if element == 0 or element == 3:
            return 'nedre grense'
        elif element == 1 or element == 2:
            return 'ovre grense'
        else:
            return None

    def get_indices_outer_boundary(self, element):
        switcher = {
            'nedre grense': (0, 3),
            'ovre grense': (1, 2),
        }
        index_point = switcher.get(self.which_outer_boundary_point(element), None)
        return index_point

    def get_index_lowest_diff_points(self, quad_index, punkt):
        diff_nth = [abs(np.sqrt(
            (punkt[0] - float(point[0])) ** 2 + (punkt[1] - float(point[1])) ** 2)) for
            point in self.nth_quad[quad_index]]
        sorted_diff_nth = sorted(diff_nth)
        index_lowest_diff = [diff_nth.index(sorted_diff_nth[1]), diff_nth.index(sorted_diff_nth[0])]
        return index_lowest_diff

    def get_linfunc_outer_boundary(self, element):
        indices_points_outer_boundary = self.get_indices_outer_boundary(element)
        a_line = (self.punkter_ytre[indices_points_outer_boundary[0]][1] -
                  self.punkter_ytre[indices_points_outer_boundary[1]][1]) / (
                         self.punkter_ytre[indices_points_outer_boundary[0]][0] -
                         self.punkter_ytre[indices_points_outer_boundary[1]][0])
        b_line = self.punkter_ytre[indices_points_outer_boundary[0]][1] - a_line * \
                 self.punkter_ytre[indices_points_outer_boundary[0]][0]
        return a_line, b_line

    def calculate_inner_points(self, a_line, b_line):
        a = a_line ** 2 + 1
        b = 2 * a_line * b_line
        c = b_line ** 2 - self.diameter ** 2 / 4
        x_pos = (-b + np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
        x_neg = (-b - np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
        y_pos = a_line * x_pos + b_line
        y_neg = a_line * x_neg + b_line
        point_pos = [x_pos, y_pos]
        point_neg = [x_neg, y_neg]
        return point_pos, point_neg

    def get_theoretical_inner_points(self, element):
        a_line_nedre, b_line_nedre = self.get_linfunc_outer_boundary(element)
        point_pos, point_neg = self.calculate_inner_points(a_line_nedre, b_line_nedre)
        points = [point_pos, point_neg]
        return points

    def calculate_intersection(self, punkt, element):
        quad_index = self.get_quad_index(punkt)
        index_lowest_diff = self.get_index_lowest_diff_points(quad_index, punkt)
        a_circ = (self.nth_quad[quad_index][index_lowest_diff[1]][1] - self.nth_quad[quad_index][index_lowest_diff[0]][
            1]) / (
                         self.nth_quad[quad_index][index_lowest_diff[1]][0] -
                         self.nth_quad[quad_index][index_lowest_diff[0]][0])
        b_circ = self.nth_quad[quad_index][index_lowest_diff[1]][1] - a_circ * \
                 self.nth_quad[quad_index][index_lowest_diff[1]][0]
        a_line, b_line = self.get_linfunc_outer_boundary(element)
        x = (b_circ - b_line) / (a_line - a_circ)
        y = (b_circ * a_line - b_line * a_circ) / (a_line - a_circ)
        point = [x, y]
        return point

    def get_points_on_circular_boundary_2(self):
        points = []
        k = [3, 1]
        path = mplt_path.Path(self.points_tunnel_boundary)
        for i in range(self.ant_linjer):
            inside = path.contains_point(((self.punkter_ytre[i][0] + self.punkter_ytre[i + k[i]][0]) / 2,
                                          (self.punkter_ytre[i][1] + self.punkter_ytre[i + k[i]][1]) / 2))
            if inside:
                points_theoretical = self.get_theoretical_inner_points(i)
                point = self.calculate_intersection(points_theoretical[0], i)
                point1 = self.calculate_intersection(points_theoretical[1], i)
                points.append(point)
                points.append(point1)
            else:
                point, point1 = None, None
                points.append(point)
                points.append(point1)
        p = points.copy()
        points = [p[0], p[2], p[3], p[1]]
        return points

    def get_start_quad(self, punkt):
        switcher = {
            '4th quad': 0,
            '1st quad': 91,
            '2nd quad': 182,
            '3rd quad': 273,
        }
        return switcher.get(self.which_quad(punkt), None)

    def sort_boundary_points(self):
        points = self.get_points_on_circular_boundary_2()
        points = [value for value in points if value is not None]
        i_data_list = []
        for i in range(len(points)):
            quad_index = self.get_quad_index(points[i])
            index_lowest_diff = self.get_index_lowest_diff_points(quad_index, points[i])
            index_lowest_diff.sort()
            i_data_list.append(self.index_boundary1 + self.get_start_quad(points[i]) + index_lowest_diff[1])
        i_data_list, points = (list(t) for t in zip(*sorted(zip(i_data_list, points))))
        self.n_points_ib = self.n_points_ib + len(points)
        return i_data_list, points

    def set_inner_boundary(self):
        i_data_list, points = self.sort_boundary_points()
        p = 0
        for i in range(len(points)):
            self.data.insert(i_data_list[i] + p,
                             "         {}: ".format(0) + str(points[i][0]) + ', ' + str(points[i][1]) + '\n')
            self.data.insert(i_data_list[i] + self.n_points_ib + 10, "        vertex 0 is temp: no" + '\n')
            p += 1
        self.data[self.index_boundary1 - 1] = re.sub(r'^(\s*(?:\S+\s+){2})\S+', r'\g<1>' + str(self.n_points_ib),
                                                     self.data[self.index_boundary1 - 1])
        # rette opp i nummerering av punkter
        for index in range(self.n_points_ib):
            self.data[self.index_boundary1 + index] = re.sub(r'^(\s*(?:\S+\s+){0})\S+', r'\g<1>' + str(index) + ':',
                                                             self.data[self.index_boundary1 + index])[1:]
            self.data[self.index_boundary1 + self.n_points_ib + 10 + index] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                                                     r'\g<1>' + str(index),
                                                                                     self.data[
                                                                                         self.index_boundary1 + self.n_points_ib + 10 + index])
        return


class OuterBoundary:
    def __init__(self, punkter_ytre, data, index_boundary2, vinkel, ant_pkt_ytre):
        self.punkter_ytre = punkter_ytre.copy()
        self.data = data
        self.index_boundary2 = index_boundary2
        self.ant_pkt_ytre = ant_pkt_ytre
        if vinkel != 0:
            self.del_points()
            self.set_points_outer_boundary()

    @staticmethod
    def get_linfunc(punkter):
        a_line = (punkter[0][1] - punkter[1][1]) / (punkter[0][0] - punkter[1][0])
        b_line = punkter[0][1] - a_line * punkter[0][0]
        return a_line, b_line

    @staticmethod
    def find_points_on_outer_boundary(point_r, point_l, ytre_grenser, ant_linjer):
        point_r = np.array(point_r)
        point_l = np.array(point_l)
        test = [ytre_grenser, -ytre_grenser]
        a = (point_r[1] - point_l[1]) / (point_r[0] - point_l[0])
        b = point_r[1] - a * point_r[0]
        point = []
        # finder hvilken begrænsning som gjelder for de to punkter som bæskriver linja og lagrer den ferdige
        # beskrivelsen i en vector
        for i in range(ant_linjer):
            y = a * test[i] + b
            x = (test[i] - b) / a
            if abs(y) <= ytre_grenser:
                point.append(np.array([test[i], y]))
            if abs(x) <= ytre_grenser:
                point.append(np.array([x, test[i]]))
        # sørger for at det endrede punkt til høyre er lagret i første element av vektoren
        v = np.sqrt(np.dot(np.linalg.norm(point[0] - point_r), (np.linalg.norm(point[0] - point_r))))
        v2 = min(np.sqrt(np.dot(np.linalg.norm(point[0] - point_r), (np.linalg.norm(point[0] - point_r)))),
                 np.sqrt(np.dot(np.linalg.norm(point[1] - point_r), (np.linalg.norm(point[1] - point_r)))))
        if v != v2:
            point = [point[1], point[0]]
        return point[0].tolist(), point[1].tolist()

    @staticmethod
    def check_points_ob(punkter_over, punkter_under):
        a, b = OuterBoundary.get_linfunc(punkter_over)
        c, d = OuterBoundary.get_linfunc(punkter_under)
        func1 = [-abs(a), abs(b)]
        func2 = [-abs(c), abs(d)]
        check = [abs(func1[0] * 150 + func1[1]), abs((150 - func1[1]) / func1[0]), abs(func2[0] * 150 + func2[1]),
                 abs((150 - func2[1]) / func2[0])]
        if any(z <= 150 for z in check[0:2]) and any(z <= 150 for z in check[2:4]):
            return False
        else:
            return True

    def which_line(self, element):
        if self.punkter_ytre[element][1] == -150 and -150 < self.punkter_ytre[element][0] <= 150:
            return '1st line'
        elif self.punkter_ytre[element][0] == 150 and -150 < self.punkter_ytre[element][1] <= 150:
            return '2nd line'
        elif self.punkter_ytre[element][1] == 150 and -150 <= self.punkter_ytre[element][0] < 150:
            return '3rd line'
        elif self.punkter_ytre[element][0] == -150 and -150 <= self.punkter_ytre[element][1] < 150:
            return '4th line'
        else:
            return None

    def get_boundary_index(self, element):
        switcher = {
            '1st line': 1,
            '2nd line': 2,
            '3rd line': 3,
            '4th line': 4,
        }
        return switcher.get(OuterBoundary.which_line(self, element), None)

    def del_points(self):
        self.data.pop(self.index_boundary2 + 7)
        self.data.pop(self.index_boundary2 + 6)
        self.data.pop(self.index_boundary2 + 3)
        self.data.pop(self.index_boundary2 + 2)

    @staticmethod
    def key_sorter(item):
        if item[0] == -150 and -150 <= item[1] < 150:
            return item[1] * -1
        elif item[1] == 150 and -150 <= item[0] < 150:
            return item[0] * -1
        elif item[0] == 150 and -150 < item[1] <= 150:
            return item[1]
        elif item[1] == -150 and -150 < item[0] <= 150:
            return item[0]
        else:
            return False

    def sort_ob_points(self, item):
        item, self.punkter_ytre = (list(t) for t in zip(*sorted(zip(item, self.punkter_ytre), reverse=True)))
        for i in range(4, 0, -1):
            indices = [j for j, x in enumerate(item) if x == i]
            if len(indices) > 1:
                to_sort = self.punkter_ytre[indices[0]:indices[-1] + 1]
                self.punkter_ytre[indices[0]:indices[-1] + 1] = sorted(to_sort, key=self.key_sorter)
        return item

    def set_points_outer_boundary(self):
        placement_new_point = []
        for i in range(self.ant_pkt_ytre):
            placement_new_point.append(self.get_boundary_index(i))
        placement_new_point = self.sort_ob_points(placement_new_point)
        dummy = placement_new_point.copy()
        k = 1
        for i in range(0, self.ant_pkt_ytre):
            if i > 0 and placement_new_point[i] == dummy[i - 1]:
                placement_new_point[i] += k
                k += 1
            else:
                k = 1
            self.data.insert(placement_new_point[i] + self.index_boundary2,
                             "        {}: ".format(0) + str(self.punkter_ytre[i][0]) + ', ' + str(
                                 self.punkter_ytre[i][1]) + '\n')
        for index in range(len(self.data[self.index_boundary2:(self.index_boundary2 + 8)])):
            self.data[self.index_boundary2 + index] = re.sub(r'^(\s*(?:\S+\s+){0})\S+', r'\g<1>' + str(index) + ':',
                                                             self.data[self.index_boundary2 + index])
        return


class BoundaryLines:
    def __init__(self, punkter_ytre, punkter_indre, index_boundary3, index_boundary4, data, ant_linjer):
        self.index_boundary3 = index_boundary3
        self.index_boundary4 = index_boundary4
        self.punkter_ytre = punkter_ytre
        self.punkter_indre = punkter_indre
        self.data = data
        self.ant_linjer = ant_linjer

    @staticmethod
    def inner_points_cleanup(punkter):
        for i in range(2):
            v3 = np.sqrt(np.dot(np.linalg.norm(np.array(punkter[0]) - np.array(punkter[1])),
                                (np.linalg.norm(np.array(punkter[0]) - np.array(punkter[1])))))
            v4 = np.sqrt(np.dot(np.linalg.norm(np.array(punkter[0]) - np.array(punkter[2])),
                                (np.linalg.norm(np.array(punkter[0]) - np.array(punkter[2])))))
            if v3 > v4:
                x = punkter.copy()
                punkter[2] = x[1]
                punkter[1] = x[2]
        return punkter

    def sort_weakness_points(self):
        punkter = []
        p = [3, 1]
        for i in range(len(p)):
            punkt = [self.punkter_ytre[i], self.punkter_indre[i], self.punkter_indre[i + p[i]],
                     self.punkter_ytre[i + p[i]]]
            if punkt[1] is not None:
                punkt = self.inner_points_cleanup(punkt)
            punkter.append(punkt)
        return punkter

    def set_weakness_points(self):
        punkter = self.sort_weakness_points()
        if all(elem is None for elem in self.punkter_indre):
            self.set_weakness_exl_inner_points()
        elif all(elem is not None for elem in self.punkter_indre):
            self.set_weakness_with_inner_points(punkter)
        else:
            self.set_weakness_with_inner_point(punkter)
        return

    def set_weakness_with_inner_points(self, punkter):
        punkter_under = punkter[0]
        punkter_over = punkter[1]
        for i in range(len(punkter_over)):
            self.data[self.index_boundary3 + i] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                         r'\g<1>' + str(punkter_under[i][0]) + ',',
                                                         self.data[self.index_boundary3 + i])
            self.data[self.index_boundary3 + i] = re.sub(r'^(\s*(?:\S+\s+){2})\S+', r'\g<1>' + str(punkter_under[i][1]),
                                                         self.data[self.index_boundary3 + i])
            self.data[self.index_boundary4 + i] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                         r'\g<1>' + str(punkter_over[i][0]) + ',',
                                                         self.data[self.index_boundary4 + i])
            self.data[self.index_boundary4 + i] = re.sub(r'^(\s*(?:\S+\s+){2})\S+', r'\g<1>' + str(punkter_over[i][1]),
                                                         self.data[self.index_boundary4 + i])
        return

    def set_weakness_with_inner_point(self, punkter):
        index_boundary = [self.index_boundary4, self.index_boundary3]
        p = [3, 1]
        for i in range(len(punkter)):
            if punkter[i][1] is not None:
                for j in range(len(punkter[i])):
                    self.data[index_boundary[i] + j] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                              r'\g<1>' + str(punkter[i][j][0]) + ',',
                                                              self.data[index_boundary[i] + j])
                    self.data[index_boundary[i] + j] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                                              r'\g<1>' + str(punkter[i][j][1]),
                                                              self.data[index_boundary[i] + j])
            else:
                self.data.pop(index_boundary[i] + 17)
                self.data.pop(index_boundary[i] + 16)
                self.data.pop(index_boundary[i] + 2)
                self.data.pop(index_boundary[i] + 1)
                self.data[index_boundary[i] + 1] = re.sub(r'^(\s*(?:\S+\s+){0})\S+', r'\g<1>' + '1:',
                                                          self.data[index_boundary[i] + 1])
                self.data[index_boundary[i] + 1] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                          r'\g<1>' + str(self.punkter_ytre[i + p[i]][0]) + ',',
                                                          self.data[index_boundary[i] + 1])
                self.data[index_boundary[i] + 1] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                                          r'\g<1>' + str(self.punkter_ytre[i + p[i]][1]),
                                                          self.data[index_boundary[i] + 1])
                self.data[index_boundary[i]] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                      r'\g<1>' + str(self.punkter_ytre[i][0]) + ',',
                                                      self.data[index_boundary[i]])
                self.data[index_boundary[i]] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                                      r'\g<1>' + str(self.punkter_ytre[i][1]),
                                                      self.data[index_boundary[i]])
                self.data[index_boundary[i] - 1] = re.sub(r'^(\s*(?:\S+\s+){2})\S+', r'\g<1>' + '2',
                                                          self.data[index_boundary[i] - 1])
        return

    def get_middle_points(self):
        p = []
        for i in range(self.ant_linjer):
            k = [3, 1]
            p.append(((self.punkter_ytre[i][0] + self.punkter_ytre[i + k[i]][0]) / 2,
                      (self.punkter_ytre[i][1] + self.punkter_ytre[i + k[i]][1]) / 2))
        return p

    def set_weakness_exl_inner_points(self):
        index_boundary = [self.index_boundary4, self.index_boundary3]
        middlepoints = self.get_middle_points()
        p = [3, 1]
        for i in range(len(index_boundary)):
            self.data.pop(index_boundary[i] + 17)
            self.data.pop(index_boundary[i] + 2)
            self.data[index_boundary[i] + 1] = re.sub(r'^(\s*(?:\S+\s+){0})\S+', r'\g<1>' + '1:',
                                                      self.data[index_boundary[i] + 1])
            self.data[index_boundary[i] + 1] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                      r'\g<1>' + str(middlepoints[i][0]) + ',',
                                                      self.data[index_boundary[i] + 1])
            self.data[index_boundary[i] + 1] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                                      r'\g<1>' + str(middlepoints[i][1]),
                                                      self.data[index_boundary[i] + 1])
            self.data[index_boundary[i] + 2] = re.sub(r'^(\s*(?:\S+\s+){0})\S+', r'\g<1>' + '2:',
                                                      self.data[index_boundary[i] + 2])
            self.data[index_boundary[i] + 2] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                      r'\g<1>' + str(self.punkter_ytre[i + p[i]][0]) + ',',
                                                      self.data[index_boundary[i] + 2])
            self.data[index_boundary[i] + 2] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                                      r'\g<1>' + str(self.punkter_ytre[i + p[i]][1]),
                                                      self.data[index_boundary[i] + 2])
            self.data[index_boundary[i]] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                  r'\g<1>' + str(self.punkter_ytre[i][0]) + ',',
                                                  self.data[index_boundary[i]])
            self.data[index_boundary[i]] = re.sub(r'^(\s*(?:\S+\s+){2})\S+', r'\g<1>' + str(self.punkter_ytre[i][1]),
                                                  self.data[index_boundary[i]])
            self.data[index_boundary[i] - 1] = re.sub(r'^(\s*(?:\S+\s+){2})\S+', r'\g<1>' + '3',
                                                        self.data[index_boundary[i] - 1])
        return


class Materials(InnerBoundary):
    def __init__(self, index_materials, punkter_indre, ytre_grense, ant_linjer, nth_quad, punkter_ytre, data,
                 number_points_inner_boundary, index_boundary1,
                 diameter, vinkel, points_tunnel_boundary):
        super().__init__(ant_linjer, nth_quad, punkter_ytre, data, number_points_inner_boundary, index_boundary1,
                         diameter, vinkel, points_tunnel_boundary)
        self.index_materials = index_materials
        self.punkter_indre = punkter_indre.copy()
        self.ytre_grense = ytre_grense

    def setmaterialmesh(self):
        if all(points is None for points in self.punkter_indre):
            self.__setmaterialmesh0()
        elif any(points is None for points in self.punkter_indre):
            self.__setmaterialmesh1()
        else:
            self.__setmaterialmesh2()
        return

    def __setmaterialmesh0(self):
        del self.data[self.index_materials + 36:self.index_materials + 63]
        i_material = self.index_materials
        normaler = self.get_normal_lines()
        ytre_punkt_under, ytre_punkt_over = self.checker_ob_exl_innerb(normaler)
        print(ytre_punkt_over, ytre_punkt_under)
        list_iterate, list_iterate1 = self.__get_material_list0(ytre_punkt_under, ytre_punkt_over)
        self.data[i_material - 2] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                           r'\g<1>' + str(4),
                                           self.data[i_material - 2])
        for i in range(4):
            for j in range(3):
                self.data[i_material + j + 1] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                       r'\g<1>' + str(list_iterate[i][j][0]) + ',',
                                                       self.data[i_material + j + 1])
                self.data[i_material + j + 1] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                                       r'\g<1>' + str(list_iterate[i][j][1]),
                                                       self.data[i_material + j + 1])
                self.data[i_material + 5] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                                   r'\g<1>' + str(list_iterate1[i][0]),
                                                   self.data[i_material + 5])
                self.data[i_material + 6] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                                   r'\g<1>' + str(list_iterate1[i][1]),
                                                   self.data[i_material + 6])
            i_material += 9
        return

    def __get_material_list0(self, ytre_punkt_under, ytre_punkt_over):
        list = [[self.punkter_ytre[0], self.punkter_ytre[3], ytre_punkt_under],
                [self.punkter_ytre[1], self.punkter_ytre[2], ytre_punkt_over],
                [self.punkter_ytre[3], self.punkter_ytre[2], self.punkter_ytre[1]],
                [self.points_tunnel_boundary[0], self.points_tunnel_boundary[180], self.points_tunnel_boundary[270]]]
        list1 = [[15, 15], [15, 15], [16, 16], [15, 0]]
        return list, list1

    def __setmaterialmesh1(self):
        del self.data[self.index_materials + 45:self.index_materials + 63]
        if self.vinkel == 0:
            ytre_punkt_over = [0, 150]
            ytre_punkt_under = [0, -150]
            if self.punkter_indre[0] is not None:
                punkt_i_sone, punkt_u_sone = [0, 5], [0, -5]
            else:
                punkt_i_sone, punkt_u_sone = [0, -5], [0, 5]
        else:
            normaler = self.get_normal_lines()
            middlepoints = self.get_middle_points()
            under, over = middlepoints[0], middlepoints[1]
            if self.origo_is_between(under, over):
                ytre_punkt_under = self.checker_ob(normaler[0], 0)
                ytre_punkt_over = self.checker_ob(normaler[1], 1)
            else:
                ytre_punkt_under, ytre_punkt_over = self.checker_ob_exl_innerb(normaler)
            if self.punkter_indre[0] is not None:
                punkt_i_sone, punkt_u_sone = self.checker_ib(normaler[0], 0)
            else:
                punkt_i_sone, punkt_u_sone = self.checker_ib(normaler[1], 1)
        list_iterate, list_iterate1 = self.__get_material_list1(ytre_punkt_under, ytre_punkt_over, punkt_i_sone, punkt_u_sone)
        print(list_iterate)
        i_material = self.index_materials
        self.data[i_material - 2] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                           r'\g<1>' + str(5),
                                           self.data[i_material - 2])
        for i in range(5):
            for j in range(3):
                self.data[i_material + j + 1] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                       r'\g<1>' + str(list_iterate[i][j][0]) + ',',
                                                       self.data[i_material + j + 1])
                self.data[i_material + j + 1] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                                       r'\g<1>' + str(list_iterate[i][j][1]),
                                                       self.data[i_material + j + 1])
            self.data[i_material + 5] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                               r'\g<1>' + str(list_iterate1[i][0]),
                                               self.data[i_material + 5])
            self.data[i_material + 6] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                               r'\g<1>' + str(list_iterate1[i][1]),
                                               self.data[i_material + 6])
            i_material += 9
        return

    def __get_opposite_circb_point(self, element):
        middlepoint = self.get_middle_point(element)
        q = [elem for elem in self.punkter_indre if elem is not None]
        r = [round(q[0][0], 17), round(q[0][1], 17)]
        r = self.points_tunnel_boundary.index(r)
        s = [round(q[1][0], 17), round(q[1][1], 17)]
        s = self.points_tunnel_boundary.index(s)
        u = round((r + s) / 2)
        point = self.points_tunnel_boundary[u]
        return point

    def __get_material_list1(self, ytre_punkt_under, ytre_punkt_over, punkt_i_sone, punkt_u_sone):
        # q til u, finne et punkt på tunnel boundary som gjør at materialmeshet for dette materialet blir veldefinert
        p = [3, 2]
        if self.punkter_indre[0] is not None:
            i = 0
        else:
            i = 1
        list = [[self.punkter_ytre[0], self.punkter_ytre[3], ytre_punkt_under],
                [self.punkter_ytre[1], self.punkter_ytre[2], ytre_punkt_over],
                [self.punkter_indre[i], self.punkter_indre[p[i]], punkt_i_sone],
                [self.punkter_indre[i], self.punkter_indre[p[i]], punkt_u_sone],
                [self.punkter_ytre[3], self.punkter_ytre[2], self.punkter_indre[p[i]]]]
        list1 = [[15, 15], [15, 15], [16, 0], [15, 0], [16, 16]]
        return list, list1

    def get_middle_point(self, element):
        k = [3, 1]
        middlepoint = ((self.punkter_ytre[element][0] + self.punkter_ytre[element + k[element]][0]) / 2,
                       (self.punkter_ytre[element][1] + self.punkter_ytre[element + k[element]][1]) / 2)
        return middlepoint

    @staticmethod
    def get_normal_line(a0, midpoint):
        a, b = -(1 / a0), midpoint[1] + (midpoint[0] / a0)
        return [a, b]

    @staticmethod
    def origo_is_between(middlepoint_under, middlepoint_over):
        origo = [0, 0]
        epsilon = 10**-13
        crossproduct = (origo[1] - middlepoint_under[1]) * (middlepoint_over[0] - middlepoint_under[0]) - (
                origo[0] - middlepoint_under[0]) * (middlepoint_over[1] - middlepoint_under[1])
        # compare versus epsilon for floating point values, or != 0 if using integers
        if abs(crossproduct) > epsilon:
            return False
        dotproduct = (origo[0] - middlepoint_under[0]) * (middlepoint_over[0] - middlepoint_under[0]) + (origo[1] - middlepoint_under[1]) * (middlepoint_over[1] - middlepoint_under[1])
        if dotproduct < 0:
            return False
        squaredlengthba = (middlepoint_over[0] - middlepoint_under[0]) ** 2 + (middlepoint_over[1] - middlepoint_under[1]) ** 2
        if dotproduct > squaredlengthba:
            return False
        return True

    def get_normal_lines(self):
        mid_points = self.get_middle_points()
        a0, b0 = self.get_linfunc_outer_boundary(0)
        normal_under = self.get_normal_line(a0, mid_points[0])
        c0, d0 = self.get_linfunc_outer_boundary(1)
        normal_over = self.get_normal_line(c0, mid_points[1])
        return [normal_under, normal_over]

    @staticmethod
    def key_checker(elem):
        return abs(elem[0])

    def checker_ob(self, normal, element):
        middlepoint = self.get_middle_point(element)
        points = [self.ytre_grense, normal[0] * self.ytre_grense + normal[1]], [-self.ytre_grense,
                                                                                normal[0] * -self.ytre_grense + normal[
                                                                                    1]]
        check = [np.sqrt((points[0][0] - middlepoint[0]) ** 2 + (points[0][1] - middlepoint[1]) ** 2),
                 np.sqrt((points[1][0] - middlepoint[0]) ** 2 + (points[1][1] - middlepoint[1]) ** 2)]
        check, point = [list(t) for t in zip(*sorted(zip(check, points)))]
        point = point[0]
        return point

    def checker_ob_exl_innerb(self, normal):
        under = 0
        over = 1
        middlepoint_under = self.get_middle_point(under)
        middlepoint_over = self.get_middle_point(over)
        points_under = [self.ytre_grense, normal[under][0] * self.ytre_grense + normal[under][1]], [-self.ytre_grense, normal[under][0] * -self.ytre_grense + normal[under][1]]
        points_over = [self.ytre_grense, normal[over][0] * self.ytre_grense + normal[over][1]], [-self.ytre_grense, normal[over][0] * -self.ytre_grense + normal[over][1]]
        check_under = [np.sqrt(
            (points_under[0][0] - middlepoint_under[0]) ** 2 + (points_under[0][1] - middlepoint_under[1]) ** 2),
            np.sqrt((points_under[1][0] - middlepoint_under[0]) ** 2 + (
                    points_under[1][1] - middlepoint_under[1]) ** 2)]
        check_over = [
            np.sqrt((points_over[0][0] - middlepoint_over[0]) ** 2 + (points_over[0][1] - middlepoint_over[1]) ** 2),
            np.sqrt((points_over[1][0] - middlepoint_over[0]) ** 2 + (points_over[1][1] - middlepoint_over[1]) ** 2)]
        check_under, points_under = [list(t) for t in zip(*sorted(zip(check_under, points_under)))]
        check_over, points_over = [list(t) for t in zip(*sorted(zip(check_over, points_over)))]
        if check_under[0] < check_over[0]:
            point_under = points_under[0]
            point_over = points_over[1]
        else:
            point_under = points_under[1]
            point_over = points_over[0]
        return point_under, point_over

    def checker_ib(self, normal, element):
        middlepoint = self.get_middle_point(element)
        middlepoints = self.get_middle_points()
        point_pos, point_neg = self.calculate_inner_points(normal[0], normal[1])
        points = [point_pos, point_neg]
        q = self.calculate_intersection_ib(point_pos, normal)
        p = self.calculate_intersection_ib(point_neg, normal)
        check = [np.sqrt((q[0] - middlepoint[0]) ** 2 + (q[1] - middlepoint[1]) ** 2),
                 np.sqrt((p[0] - middlepoint[0]) ** 2 + (p[1] - middlepoint[1]) ** 2)]
        check, point = [list(t) for t in zip(*sorted(zip(check, points)))]
        if self.origo_is_between(middlepoints[0], middlepoints[1]):
            point_weakness = point[1]
            point_exl_weakness = point[0]
        else:
            point_weakness = point[0]
            point_exl_weakness = point[1]

        return point_weakness, point_exl_weakness

    def checker_ib_centered(self, normal, element):
        middlepoint = self.get_middle_point(element)
        point_pos, point_neg = self.calculate_inner_points(normal[0], normal[1])
        points = [point_pos, point_neg]
        q = self.calculate_intersection_ib(point_pos, normal)
        p = self.calculate_intersection_ib(point_neg, normal)
        check = [np.sqrt((q[0] - middlepoint[0]) ** 2 + (q[1] - middlepoint[1]) ** 2),
                 np.sqrt((p[0] - middlepoint[0]) ** 2 + (p[1] - middlepoint[1]) ** 2)]
        check, point = [list(t) for t in zip(*sorted(zip(check, points)))]

        point = point[0]
        print(point)
        return point

    def calculate_intersection_ib(self, punkt, normal):
        quad_index = self.get_quad_index(punkt)
        index_lowest_diff = self.get_index_lowest_diff_points(quad_index, punkt)
        a_circ = (self.nth_quad[quad_index][index_lowest_diff[1]][1] - self.nth_quad[quad_index][index_lowest_diff[0]][
            1]) / (
                         self.nth_quad[quad_index][index_lowest_diff[1]][0] -
                         self.nth_quad[quad_index][index_lowest_diff[0]][0])
        b_circ = self.nth_quad[quad_index][index_lowest_diff[1]][1] - a_circ * \
                 self.nth_quad[quad_index][index_lowest_diff[1]][0]
        x = (b_circ - normal[1]) / (normal[0] - a_circ)
        y = (b_circ * normal[0] - normal[1] * a_circ) / (normal[0] - a_circ)
        point = [x, y]
        return point

    def __get_material_list2(self, ytre_punkt_under, ytre_punkt_over, indre_punkt_under, indre_punkt_over):
        list = [[self.punkter_ytre[0], self.punkter_ytre[3], ytre_punkt_under],
                [self.punkter_ytre[1], self.punkter_ytre[2], ytre_punkt_over],
                [self.punkter_indre[0], self.punkter_indre[3], indre_punkt_under],
                [self.punkter_indre[1], self.punkter_indre[2], indre_punkt_over],
                [self.punkter_ytre[3], self.punkter_ytre[2], self.punkter_indre[2]],
                [self.punkter_ytre[0], self.punkter_ytre[1], self.punkter_indre[1]],
                [self.punkter_indre[3], self.punkter_indre[2], self.punkter_indre[1]]]
        list1 = [[15, 15], [15, 15], [15, 0], [15, 0], [16, 16], [16, 16], [16, 0]]
        return list, list1

    def __setmaterialmesh2(self):
        normaler = self.get_normal_lines()
        ytre_punkt_under = self.checker_ob(normaler[0], 0)
        ytre_punkt_over = self.checker_ob(normaler[1], 1)
        indre_punkt_under = self.checker_ib_centered(normaler[0], 0)
        indre_punkt_over = self.checker_ib_centered(normaler[1], 1)
        list_iterate, list_iterate1 = self.__get_material_list2(ytre_punkt_under, ytre_punkt_over, indre_punkt_under,
                                                                indre_punkt_over)
        i_material = self.index_materials
        for i in range(7):
            for j in range(3):
                self.data[i_material + j + 1] = re.sub(r'^(\s*(?:\S+\s+){1})\S+',
                                                       r'\g<1>' + str(list_iterate[i][j][0]) + ',',
                                                       self.data[i_material + j + 1])
                self.data[i_material + j + 1] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                                       r'\g<1>' + str(list_iterate[i][j][1]),
                                                       self.data[i_material + j + 1])
            self.data[i_material + 5] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                               r'\g<1>' + str(list_iterate1[i][0]),
                                               self.data[i_material + 5])
            self.data[i_material + 6] = re.sub(r'^(\s*(?:\S+\s+){2})\S+',
                                               r'\g<1>' + str(list_iterate1[i][1]),
                                               self.data[i_material + 6])
            i_material += 9
        return
