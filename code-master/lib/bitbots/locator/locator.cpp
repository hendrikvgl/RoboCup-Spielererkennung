#include "locator.hpp"
#include "../debug/debug.hpp"
#include "image_point_to_location_transformer.hpp"

#include <Eigen/Core>

#include <vector>
#include <iostream>
#include "locator.hpp"

using namespace Location;

Line_Samples Locator::make_field_model()//Wenn Feldmodell geändert wird Line_Matcher::match_samples anpassen
{
	std::vector<Line>* lines = new std::vector<Line>();
	Line linke_aussenlinie(Eigen::Vector2f(-3,2), Eigen::Vector2f(3,2), Eigen::Vector2f(6,0));
	Line linke_strafraumgrenze_hinten(Eigen::Vector2f(-3, 1.1), Eigen::Vector2f(-2.4, 1.1), Eigen::Vector2f(0.6,0));
	Line linke_strafraumgrenze_vorne(Eigen::Vector2f(2.4, 1.1), Eigen::Vector2f(3, 1.1), Eigen::Vector2f(0.6,0));
	Line rechte_strafraumgrenze_hinten(Eigen::Vector2f(-3, -1.1), Eigen::Vector2f(-2.4, -1.1), Eigen::Vector2f(0.6,0));
	Line rechte_strafraumgrenze_vorne(Eigen::Vector2f(2.4, -1.1), Eigen::Vector2f(3, -1.1), Eigen::Vector2f(0.6,0));
	Line rechte_aussenlinie(Eigen::Vector2f(-3, -2), Eigen::Vector2f(3, -2), Eigen::Vector2f(6,0));

	Line vordere_feldlinie(Eigen::Vector2f(3, -2), Eigen::Vector2f(3, 2), Eigen::Vector2f(0, 4));
	Line vordere_strafraumgrenze(Eigen::Vector2f(2.4, -1.1), Eigen::Vector2f(2.4, 1.1), Eigen::Vector2f(0, 2.2));
	Line mittellinie(Eigen::Vector2f(0, -2), Eigen::Vector2f(0, 2), Eigen::Vector2f(0, 4));
	Line hintere_strafraumgrenze(Eigen::Vector2f(-2.4, -1.1), Eigen::Vector2f(-2.4, 1.1), Eigen::Vector2f(0, 2.2));
	Line hintere_feldlinie(Eigen::Vector2f(-3, -2), Eigen::Vector2f(-3, 2), Eigen::Vector2f(0, 4));
	//six horizontal lines
	lines->push_back(linke_aussenlinie);
	lines->push_back(linke_strafraumgrenze_hinten);
	lines->push_back(linke_strafraumgrenze_vorne);
	lines->push_back(rechte_strafraumgrenze_hinten);
	lines->push_back(rechte_strafraumgrenze_vorne);
	lines->push_back(rechte_aussenlinie);
	// five vertikal linies
	lines->push_back(hintere_feldlinie);
	lines->push_back(hintere_strafraumgrenze);
	lines->push_back(mittellinie);
	lines->push_back(vordere_strafraumgrenze);
	lines->push_back(vordere_feldlinie);

	std::vector<Circle>* circles = new std::vector<Circle>();
	Circle mittelkreis(Eigen::Vector2f(0,0), 0.6);
	circles->push_back(mittelkreis);

	std::vector<Eigen::Vector2f>* points = new std::vector<Eigen::Vector2f>();
	Eigen::Vector2f vorderer_elfmeterpunkt(1.2,0);
	//Eigen::Vector2f anstosspunkt = Eigen::Vector2f(0, 0);
	Eigen::Vector2f hinterer_elfmeterpunkt(-1.2,0);
	points->push_back(hinterer_elfmeterpunkt);
	//points->push_back(anstosspunkt);
	points->push_back(vorderer_elfmeterpunkt);

	return Line_Samples(*lines, *circles, *points);
}


